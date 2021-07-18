"""
    The PYDEVTS server implementation.
"""
from typing import Coroutine
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import struct
import secrets
import anyio

class Server:
    """
        Server counterpart to pydevts.connection.Connection

        Request types:
        - 0 : PYDEVTS_PING
        - 1 : PYDEVTS_PUBKEY
        - 2 : PYDEVTS_START_SECURITY
        - 3 : PYDEVTS_END_SECURITY
        - 4 : PYDEVTS_REQUEST_AUTH
        - 5 : PYDEVTS_AUTH_RESPONSE
        - 6 : PYDEVTS_REQUEST_SECURITY_EVIDENCE
        - 7 : PYDEVTS_SECURITY_EVIDENCE
    """

    def __init__(self, auth: tuple[bytes, bytes], sign: tuple[bytes, bytes]) -> "Server":
        """
            Saves keypairs.
        """
        self._auth = auth
        self._sign = sign
    
    async def initialize_with_coro(self, coro: Coroutine = None):
        """
            Awaits provided coroutine, saves returned server object in a class variable,
            and then returns self
        """
        if coro is None:
            coro = anyio.create_tcp_listener(local_host='localhost', local_port=58000)
        self._listener = await coro

        # Serve
        await self._listener.serve(self._handle_request)


    @classmethod
    async def serve(cls, handler: Coroutine, host: str = None, port: int = None, *, auth: tuple[bytes, bytes] = None, sign: tuple[bytes, bytes] = None):
        """
            Creates and intializes server and RSA keys
        """
        # Verify arguments and setup default values
        if host is None:
            host = 'localhost'
        if port is None:
            port = 58000
        if auth is None:
            # Generate RSA keypair
            auth = RSA.generate(2048)
            
        if sign is None:
            # Generate RSA keypair
            sign = RSA.generate(2048)
        auth = (auth.publickey().exportKey(), auth.exportKey())
        sign = (sign.publickey().exportKey(), sign.exportKey())
        c = cls(auth, sign)

        c._handler = handler
        
        await c.initialize_with_coro(anyio.create_tcp_listener(local_host= host, local_port= port))

        

        return c
    

    async def _handle_request(self, conn):
        """
            Handle a request.
        """
        while True:
            # Receive header
            header = await conn.receive(struct.calcsize("BLL"))

            # Unpack header
            (type, length, meta_length) = struct.unpack("BLL", header)

            # Switch on type
            if type == 0:
                # PING
                await conn.send(struct.pack("BLL", 0, 0, 0))
                print("ping")
            elif type == 1:
                # PUBKEY
                # Save pubkey in data
                
                data = self._auth[0]

                # Pack header into data
                data = struct.pack("BLL", 1, len(data), 0) + bytes(data)

                # Send data
                await conn.send(data)


                print("pubkey")
            elif type == 2:
                # START_SECURITY
                print("SS")

    async def close(self):
        """
            Closes connection
        """
        await self._connection.aclose()

    async def __aenter__(self):
        """
            Enter the server context.
        """
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
            Exit the server context.
        """
        await self.close()
    

