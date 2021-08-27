"""
    Implements a TCP connection wrapper
"""

# TCP sockets
import anyio

# Type hints
from anyio.abc._sockets import SocketStream

class TCPConn:
    """
        Implements a TCP connection wrapper
    """

    _conn: SocketStream

    def __init__(self, wraps: SocketStream = None):
        """Initialize the class

        Args:
            wraps (SocketStream, optional): socket stream to wrap. Defaults to None
        """

        # Initialize socket stream to None
        self._conn = wraps
    
    async def connect(self, host: str, port: int):
        """Connect to a remote host
        
        Args:
            host: host to connect to
            port: port to connect to
        """

        # If we are already connected, raise an error
        if self._conn:
            raise RuntimeError("Already connected")
        
        # Create a new socket stream
        self._conn = await anyio.connect_tcp(host, port)
    
    async def send(self, data: bytes):
        """Send data over the connection

        Args:
            data: data to send
        """

        # If we are not connected, raise an error
        if not self._conn:
            raise RuntimeError("Not connected")

        await self._conn.send(data)
    
    async def recv(self, max_bytes: int = 65536) -> bytes:
        """Receive data over the connection

        Args:
            max_bytes (int, optional): maximum number of bytes to receive. Defaults to 65536

        Returns:
            bytes: data received
        """

        # If we are not connected, raise an error
        if not self._conn:
            raise RuntimeError("Not connected")

        return await self._conn.receive(max_bytes=max_bytes)
    
    async def close(self):
        """Close the connection
        """


        # If we are connected, close
        if self._conn:
            await self._conn.aclose()
            self._conn = None
    
    
        
