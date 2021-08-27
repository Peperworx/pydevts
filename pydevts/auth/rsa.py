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
        Authentication method that uses a RSA keypair and random symmetric key.
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

        # Generate random symmetric key
        key = secrets.token_bytes(16)

        # Load the public key
        pubkey = RSA.import_key(self.pubkey)

        # Load the private key
        privkey = RSA.import_key(self.privkey)

        # Encrypt the symmetric key with the public key
        cipher = PKCS1_OAEP.new(pubkey)
        enc_key = cipher.encrypt(key)

        # Send the encrypted key
        await conn.send("START_RSA", enc_key)

        # Create a new AES cipher
        cipher = AES.new(key, AES.MODE_EAX)

        # Receive the encrypted nonce
        enc_nonce = await conn.recv()

        # Verify the name sent with it
        if enc_nonce[0] != "START_AES":
            raise AuthenticationError("Invalid message received")
        
        # Decrypt the nonce
        nonce = cipher.decrypt_and_verify(enc_nonce[1], enc_nonce[2])

        # Create the private key cipher
        cipher = PKCS1_OAEP.new(privkey)

        # Encrypt it using the private key
        nenc_nonce = cipher.encrypt(nonce)

        # Send the encrypted nonce as the FINISH_RSA name
        await conn.send("FINISH_RSA", nenc_nonce)

    async def accept_handshake(self, conn: _WrappedConnection):
        """The server side version of _Auth.handshake

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        # Expect the client to send the encrypted symmetric key
        enc_key = await conn.recv()

        # Verify that the message is a START_RSA message
        if enc_key[0] != "START_RSA":
            raise AuthenticationError("Invalid message received")
        
        # If it is OK, load the private key
        privkey = RSA.import_key(self.privkey)

        # Load the public key
        pubkey = RSA.import_key(self.pubkey)

        # Decrypt the symmetric key
        cipher = PKCS1_OAEP.new(privkey)
        key = cipher.decrypt(enc_key[1])

        # Create a new AES cipher
        cipher = AES.new(key, AES.MODE_EAX)

        # Create a random value
        nonce = secrets.token_bytes(16)

        # Encrypt the nonce with the AES cipher
        ciphertext, tag = cipher.encrypt_and_digest(nonce)

        # Send the encrypted nonce
        await conn.send("START_AES", ciphertext, tag)

        # Receive the encrypted nonce
        enc_nonce = await conn.recv()

        # Verify the name sent with it
        if enc_nonce[0] != "FINISH_RSA":
            raise AuthenticationError("Invalid message received")
        
        # Create the public key cipher
        cipher = PKCS1_OAEP.new(privkey)

        # Decrypt the nonce with the public key
        dec_nonce = cipher.decrypt(enc_nonce[1])

        # Verify the integrity of the value
        if dec_nonce != nonce:
            raise AuthenticationError("Invalid nonce received")


    
