"""
    Provides a basic routing system
"""
from ._base import RouterBase
from typing import Optional
from loguru import logger
import msgpack
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import anyio
import struct

class BasicRouter(RouterBase):


    """
        Message type:
        0. Ping
        1. Info Request
        2. Info Response
        3. Start Encryption
        4. Verify Encryption
    """

    async def prepare_security(self):
        """
            Prepares security keys.
        """
        

        # Generate encryption keys
        self.enc_key = RSA.generate(2048)
        
        # Generate signing keys
        self.sign_key = RSA.generate(2048)

       


    async def connect_to(self, host: str, port: int):
        """
            Executed when node is attempting to connect to cluster
            Arguments
            - {host}
                Host of the entry node
            - {port}
                Port of the entry node
        """

        # If at any time the connection fails, log and exit.

        # Try to connect to host and port, and return none if 
        # OSError is raised.
        try:
            conn = await anyio.connect_tcp(host, port)
        except OSError:
            logger.debug(f"Failed to connect to {host}:{port}")
            return None
        
        

        # Ping host online
        await conn.send(struct.pack("LBLL",0xBEEFF00D,0,0,0))

        # Await response
        data = await conn.receive(struct.calcsize("LBLL"))
        
        # Unpack data
        header = struct.unpack("LBLL", data[:32])

        # Verify response
        if header != (0xBEEFF00D,0,0,0):
            logger.debug(f"Failed to enter via node {host}:{port}")
            return
        
        # Request node data
        await conn.send(struct.pack("LBLL",0xBEEFF00D,1,0,0))
        
        # Await node data
        data = await conn.receive(struct.calcsize("LBLL"))

        # Unpack data
        header = struct.unpack("LBLL", data[:32])
        
        
        # Verify response
        if header[0] != 0xBEEFF00D or header[1] != 2:
            logger.debug(f"Failed to enter via node {host}:{port}")
            return

        # Pull actual data
        entry = await conn.receive(header[2])

        # Unpack data
        entry: dict = msgpack.loads(entry)

        # Set our entry node
        self.entry = entry

        # Generate random 256-bit key
        key = get_random_bytes(32)

        
        # Create request for using encryption
        data = key

        # Import encryption key
        rsakey = RSA.import_key(self.entry["enc_key"])

        # Create cipher
        cipher = PKCS1_OAEP.new(rsakey)

        # Encrypt data
        ciphertext = cipher.encrypt(data)

        # Create header
        header = struct.pack("LBLL",0xBEEFF00D,3,len(ciphertext),0)

        # Add header to ciphertext and store in data
        data = header + ciphertext

        # Send data
        await conn.send(data)

        # Await response
        data = await conn.receive(struct.calcsize("LBLL"))

        # Unpack header
        header = struct.unpack("LBLL", data[:32])

        # Verify response
        if header[0] != 0xBEEFF00D or header[1] != 4:
            
            logger.debug(f"Failed to enter via node {host}:{port}")
            return
        

        # Receive data
        data = await conn.receive(header[2])

        # Unpack data
        data: dict = msgpack.loads(data)

        # Create AES cipher using nonce from request
        cipher = AES.new(key, AES.MODE_EAX, nonce=data["nonce"])
        
        # Decrypt data
        plaintext = cipher.decrypt(data["ciphertext"])

        # Verify data using tag from response
        try:
            cipher.verify(data["tag"])
        except ValueError as e:
            
            logger.debug(f"Failed to enter via node {host}:{port}")
            return
        

        # Verify decrypted data
        if plaintext != key:
            logger.debug(f"Failed to enter via node {host}:{port}")
            return

        


        # Close connection
        await conn.aclose()
    
    async def emit(self, data: bytes):
        """
            Executed when a node wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """
        pass

    async def send(self, target: str, data: bytes):
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """
        pass
    
    async def info(self) -> dict:
        """
            Packs info into a msgpack encadable dictionary.
        """
        return {
            "nid": self.owner.nid,
            "port": self.owner.port,
            "enc_key": self.enc_key.publickey().exportKey(),
            "sign_key": self.sign_key.publickey().exportKey(),
        }

    async def receive(self, conn) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {conn}
                The Connection Object
        """
        
        # Receive data
        data = await conn.receive(struct.calcsize("LBLL"))

        # Unpack header
        header = struct.unpack("LBLL", data[:32])
        print(header)
        # Verify magic number
        if header[0] != 0xBEEFF00D:
            return None
        
        # Switch on message type
        if header[1] == 0:
            # Ping
            
            # Reply with pong
            await conn.send(struct.pack("LBLL",0xBEEFF00D,0,0,0))
        elif header[1] == 1:
            # Info Request

            # Pack data
            data = msgpack.dumps(await self.info())
            
            # Pack info response header into data
            data = struct.pack("LBLL",0xBEEFF00D,2,len(data),0) + data

            # Send data
            await conn.send(data)

        
        elif header[1] == 3:
            # Start Encryption

            # Recieve encrypted message
            data = await conn.receive(header[2])

            # Create cipher
            cipher = PKCS1_OAEP.new(self.enc_key)

            # Decrypt key
            key = cipher.decrypt(data)

            # Create AES cipher
            cipher = AES.new(key, AES.MODE_EAX)

            # Respond with message.
            # Message must be a known value by both parties, so lets
            # use the encryption key
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(key)

            # Pack data
            data = msgpack.dumps({
                "nonce": nonce,
                "ciphertext": ciphertext,
                "tag": tag,
            })

            # Pack info response header into data
            data = struct.pack("LBLL",0xBEEFF00D,4,len(data),0) + data

            # Send data
            await conn.send(data)
        else:
            # Unknown message
            return None

        


    
    
    
    