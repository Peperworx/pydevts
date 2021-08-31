"""
    Base classes for protocol implementations.
"""


# Type hints
from typing import Callable
from anyio import TASK_STATUS_IGNORED
from anyio.abc import TaskStatus

class _Conn:
    """Base class for connection classes.
    """

    def __init__(self):
        """Initialize the connection
        """

        raise NotImplementedError("This is an abstract class")
    

    async def recv(self, max_bytes: int = 35536) -> bytes:
        """Receive data overthe connection.

        Args:
            max_bytes (int, optional): Maximum number of bytes to receive. Defaults to 35536.

        Returns:
            bytes: Data received over the connection.
        """

        raise NotImplementedError("This is an abstract class")
    
    async def send(self, data: bytes):
        """Send data over the connection.

        Args:
            data (bytes): Data to send.
        """

        raise NotImplementedError("This is an abstract class")


    async def close(self):
        """Close the connection
        """

        raise NotImplementedError("This is an abstract class")


class _Client(_Conn):
    """Base class for client classes.
    """

    def __init__(self):
        """Initialise the client
        """

        raise NotImplementedError("This is an abstract class")
    
    @classmethod
    async def connect(cls, host: str, port: int) -> None:
        """Connect to a remote server.

        Args:
            host (str): Hostname or IP address.
            port (int): Port number.
        """

        raise NotImplementedError("This is an abstract class")
    

class _Server:
    """Base class for server classes.
    """

    port: int # The public port of the server
    handler: Callable[[_Conn], None] # The data handler

    def __init__(self, host: str, port: int, handler: Callable[[_Conn], None]):
        """[summary]

        Args:
            host (str): The host to listen on
            port (int): The port to listen on
            handler (Callable[[_Conn], None]): The connection handler
        """

        raise NotImplementedError("This is an abstract class")
    
    

    async def run(self, task: TaskStatus = TASK_STATUS_IGNORED):
        """Run the server.

        Args:
            ONLY PASSED BY ANYIO:
            task (TaskStatus, optional, anyio): The task status. Defaults to TASK_STATUS_IGNORED.
        """

        raise NotImplementedError("This is an abstract class")