"""
    Provides a basic routing system
"""
from ._base import RouterBase
from typing import Optional
from loguru import logger
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import anyio
import struct

class BasicRouter(RouterBase):


    """
        Message Codes:
        0. Ping
        1. Info Request
        2. Info Response
        3. Join Request
        4. Join Response
        5. Send Message
        6. Emit Message
    """

    async def security_prep(self):
        """
            Prepares security systems.
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
        await conn.send(struct.pack("BLL",0,0,0))

        # Await response
        data = await conn.recv(struct.calcsize("BLL"))

        # Verify response
        if data != (0,0,0,):
            logger.debug(f"Failed to enter via node {host}:{port}")
            return
        
        # Request node data
        await conn.send(struct.pack("BLL",1,0,0))

        # Await node data
        data = await conn.recv(struct.calcsize("BLL"))

        # Verify response
        if data[0] != 2:
            return

        # Pull actual data
        entry = await conn.recv(data[1])


        
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

    async def receive(self) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {conn}
                The Connection Object
        """
        pass
    
    
    
    