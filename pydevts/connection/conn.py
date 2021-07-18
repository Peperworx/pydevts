from typing import Coroutine
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import struct
import secrets
import anyio

class Connection:
    """
        Wraps any object that derives from pydevts.connection.stream
        and forms a PYDEVTS connection over it.

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

    def __init__(self, auth: tuple[bytes, bytes], sign: tuple[bytes, bytes]) -> "Connection":
        """
            Saves keypairs.
        """
        self._auth = auth
        self._sign = sign


    async def _secure(self):
        """
            Secures the connection using a format similar to SSL, before
            sending the initial request for authentication
        """
        
        # Ping the server with a random value, verifying the returned response
        # is a PYDEVTS_PING
        await self._connection.send(struct.pack("BLL", 0, 0, 0))

        # Read the response
        data = await self._connection.receive(struct.calcsize("BLL"))

        # Verify fields are zeroed
        if data[0] != 0 or data[1] != 0 or data[2] != 0:
            raise Exception("Server failed to initialize security")
        
        # Request the server's pubkey
        await self._connection.send(struct.pack("BLL", 1, 0, 0))

        # Receive the response header
        header = await self._connection.receive(struct.calcsize("BLL"))
        print("h")

        # Verify response type
        if header[0] != 1:
            raise Exception("Server failed to respond to info request")
        
        # Receive message body
        data = await self._connection.receive(header[1])
        # Save message body as server public key
        self._server_pubkey = data

        # Import the server's RSA public key
        self._server_pubkey = RSA.importKey(self._server_pubkey)

        # Generate a random session key
        session_key = secrets.token_bytes(32)

        # Create RSA cipher
        cipher = PKCS1_OAEP.new(self._server_pubkey)

        # Encrypt the session key with the cipher
        encrypted_session_key = cipher.encrypt(session_key)

        # Send the encrypted session key
        await self._connection.send(struct.pack("BLL", 2, len(encrypted_session_key), 0) + encrypted_session_key)

    
    async def _authenticate(self):
        """
            Sends authentication request.
        """
        pass

    async def initialize_with_coro(self, coro: Coroutine = None) -> "Connection":
        """
            Awaits provided coroutine, saves returned connection object in a class variable,
            and then returns self.
        """
        if coro is None:
            coro = anyio.connect_tcp('localhost', 58000)
        self._connection = await coro

        # Begin secure connection
        await self._secure()

        # Begin authentication
        await self._authenticate()

        return self

    @classmethod
    async def connect(cls, host: str = None, port: int = None, *, auth: tuple[bytes, bytes] = None, sign: tuple[bytes, bytes] = None) -> "Connection":
        """
            Creates a basic pydevts connection over an anyio TCP stream.
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

        await c.initialize_with_coro(anyio.connect_tcp(host, port))

        return c
    
    

    async def close(self):
        """
            Closes connection
        """
        await self._connection.aclose()

    """
        Functions for async generator
    """
    async def __aenter__(self):
        """
            Opens connection
        """
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

        

        