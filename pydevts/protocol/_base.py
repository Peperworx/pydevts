"""
    Implements basic protocol base classes.
"""
from types import CoroutineType

class PYDEVTSConnection:
    """
        Represents a connection to a client or server
    """


    async def send(self, data: bytes):
        """
            This method sends all of the data provided over the connection.
        """
        pass
    

    async def recv(self, size: int) -> bytes:
        """
            This method receives {size} data.
        """
        pass
    
    async def close(self):
        """
            This method closes the connection
        """
        pass

class PYDEVTSTransport:
    """
        Base class for all transport protocols
    """

    async def connect(self, host: str, port: int) -> "PYDEVTSConnection":
        """
            Connects to host:port and returns connection
        """
        pass

    async def serve(self, callback: CoroutineType, host: str, port: int = 0):
        """
            This method serves on the specified host and port. Used by servers
        """
        pass
    

