"""
    Authentication wrapper for connections implementing _Conn.
"""

# Our parent class
from ..proto._base import _Client


# Type hints
from typing import Callable
from anyio import TASK_STATUS_IGNORED
from anyio.abc import TaskStatus
from ..auth._base import _Auth
from ..proto._base import _Conn

class AuthClient(_Client):
    """
        Authentication wrapper for clients
    """

    _wraps: _Client
    _auth: _Auth
    _conn: _Client

    def __init__(self, wraps: _Client, auth_method: _Auth):
        """Initialize the connection
        """

        # Save the wrapped and the authentication method
        self._wraps = wraps
        self._auth = auth_method

        

    
    async def connect(self, host: str, port: int) -> None:
        """Connect to a remote server.

        Args:
            host (str): Hostname or IP address.
            port (int): Port number.
        """

        

        # Connect wraps
        self._conn = await self._wraps.connect(host, port)

        # Run handshake
        await self._auth.handshake(self._conn)

    ################################################
    # These Delegate to the underlying connection
    ################################################

    async def recv(self, max_bytes: int = 35536) -> bytes:
        """Receive data overthe connection.

        Args:
            max_bytes (int, optional): Maximum number of bytes to receive. Defaults to 35536.

        Returns:
            bytes: Data received over the connection.
        """

        return await self._conn.recv(max_bytes)
    
    async def send(self, data: bytes):
        """Send data over the connection.

        Args:
            data (bytes): Data to send.
        """

        await self._conn.send(data)


    async def close(self):
        """Close the connection
        """

        await self._conn.close()
