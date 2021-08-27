"""
    RSA key based authentication
"""

# Type hints
from ..connwrapper import _WrappedConnection
from typing import Optional

# Base class
from ._base import _Auth

# Errors
from . import AuthenticationError

# Authentication
from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.PublicKey import RSA
import secrets


class AuthRSA(_Auth):
    """
        Authentication method that uses a RSA keypair
    """

    pubkey: bytes
    privkey: bytes

    def __init__(self, pubkey: bytes, privkey: bytes):
        """Initialize the RSA authentication method

        Args:
            pubkey (bytes): RSA public key.
            privkey (bytes): RSA private key. 
        """
        
        # Save keypair
        self.pubkey = pubkey
        self.privkey = privkey

    async def handshake(self, conn: _WrappedConnection):
        """Execute the initial handshake for authentication

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        # Tell the server we are ready
        await conn.send("START_RSA", b"")

        # Receive the encrypted random number
        msg = await conn.recv()

        # Verify the name
        if msg[0] != "RSA_RAND":
            raise AuthenticationError("Invalid handshake message")
        try:
            # Decrypt the random number
            cipher = PKCS1_OAEP.new(RSA.import_key(self.privkey))
            rand = cipher.decrypt(msg[1])
        except ValueError:
            raise AuthenticationError("Invalid private key")

        # Reverse all bytes of the random number
        nrand = bytearray(rand)
        nrand.reverse()
        new_rand = bytes(nrand)

        
        # Send back
        await conn.send("RSA_RAND", new_rand)

        # AUTH: Complete

    
    async def accept_handshake(self, conn: _WrappedConnection):
        """The server side version of _Auth.handshake

        Args:
            conn (_WrappedConnection): The connection that we are using
        """
        
        # Receive initial message
        msg = await conn.recv()

        # Verify the name
        if msg[0] != "START_RSA":
            raise AuthenticationError("Invalid handshake message")
        
        # Generate a random number
        rand = secrets.token_bytes(16)

        # Encrypt the random number
        cipher = PKCS1_OAEP.new(RSA.import_key(self.pubkey))
        enc_rand = cipher.encrypt(rand)

        # Send the encrypted random number
        await conn.send("RSA_RAND", enc_rand)

        # Receive the encrypted random number
        msg = await conn.recv()

        # Verify the name
        if msg[0] != "RSA_RAND":
            raise AuthenticationError("Invalid handshake message")
        
        # Reverse rand
        nrand = bytearray(rand)
        nrand.reverse()
        new_rand = bytes(nrand)

        # Verify the random number
        if msg[1] != new_rand:
            raise AuthenticationError("Invalid handshake nonce")
        
        # AUTH: Complete


    
