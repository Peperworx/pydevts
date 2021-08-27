"""
    Provides base class for communication protocols
"""


class _Conn:
    """
        Base class for communication protocols
    """

    def __init__(self):
        """Initialize the class
        """

        raise NotImplementedError("This is an abstract class")
    
    async def connect(self, host: str, port: int):
        """Connect to a remote host
        
        Args:
            host: host to connect to
            port: port to connect to
        """

        raise NotImplementedError("This is an abstract class")
    
    async def send(self, data: bytes):
        """Send data over the connection

        Args:
            data: data to send
        """

        raise NotImplementedError("This is an abstract class")
    
    async def recv(self, max_bytes: int = 65536) -> bytes:
        """Receive data over the connection

        Returns:
            bytes: data received
        """

        raise NotImplementedError("This is an abstract class")
    
    async def close(self):
        """Close the connection
        """

        raise NotImplementedError("This is an abstract class")
    
    