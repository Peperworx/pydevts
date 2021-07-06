"""
    Provides a basic routing system
"""
from ._base import RouterBase
from typing import Optional
from loguru import logger
import msgpack
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import anyio
import struct

class BasicRouter(RouterBase):


    """
        Message type:
        0. Ping
        1. Info Request
        2. Info Response
        3. Join Request
        4. Join Response
        5. Send Message
        6. Emit Message
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


        # Create connection and request information
        conn = await anyio.connect_tcp(host, port)

        # Ping host online
        await conn.send(struct.pack("LBLL",0,0,0,0))

        # Await response
        data = await conn.recv(struct.calcsize("LBLL"))

        # Verify response
        if data != (0,0,0,):
            logger.debug(f"Failed to enter via node {host}:{port}")
            return
        
        # Request node data
        await conn.send(struct.pack("LBLL",0,1,0,0))

        # Await node data
        data = await conn.recv(struct.calcsize("LBLL"))

        # Verify response
        if data[0] != 2:
            return

        # Pull actual data
        entry = await conn.recv(data[1])

        print(entry)
        
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
        header = struct.unpack("LBLL", data[:9])

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
            data = msgpack.dumps(self.info())
            
            # Pack header into data
            data = struct.pack("LBLL",0xBEEFF00D,2,len(data),0) + data

            # Send data
            await conn.send(data)
        
        elif header[1] == 3:
            # Join Request
            pass
        elif header[1] == 4:
            # Join Response
            pass
        elif header[1] == 5:
            # Send Message
            pass
        elif header[1] == 6:
            # Emit Message
            pass
        else:
            # Unknown message
            return None

        


    
    
    
    