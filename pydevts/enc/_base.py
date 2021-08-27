"""
    Base class for encryption protocols
"""

class _Enc:
    """
        Base class for encryption protocols
    """

    def __init__(self):
        """Initialize the class
        """

        raise NotImplementedError("This is an abstract class")
    
    async def encrypt(self, data: bytes) -> bytes:
        """Encrypt data

        Args:
            data (bytes): data to encrypt
        
        Returns:
            bytes: encrypted data
        """

        raise NotImplementedError("This is an abstract class")
    
    async def decrypt(self, data: bytes) -> bytes:
        """Decrypt data

        Args:
            data (bytes): data to decrypt
        
        Returns:
            bytes: decrypted data
        """

        raise NotImplementedError("This is an abstract class")
    
    