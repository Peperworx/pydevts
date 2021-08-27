"""
    Provides a base class for routing.
"""

# Type Hints
from ..connwrapper import _WrappedConnection
from typing import Callable
import ssl


class _Router:
    """A Base class for pydevts routers
    """

    ssl_context: ssl.SSLContext

    def __init__(self, ssl_context: ssl.SSLContext = None):
        """Initialize the router

        Args:
            ssl_context (tuple[str, str], optional): The public-private ssl_context to use for encryption. Defaults to None.
        """

        self.ssl_context = ssl_context
    
    async def enter(self, host: str, port: int, host_addr: tuple[str, int], tls: bool = False, verify_key: str = None):
        """Enters a cluster

        Args:
            host (str): The entry host of the cluster
            port (int): The entry port of the cluster
            host_addr (tuple[str, int]): The address that we are hosting on
            tls (bool, optional): Whether to use TLS. Defaults to False.
            verify_key (str, optional): The verify key to use for TLS. Defaults to None.
        """

        raise NotImplementedError()
    
    async def send_to(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        raise NotImplementedError()
    
    async def emit(self, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            data (bytes): The data to emit
        """

        raise NotImplementedError()
    
    async def register_handler(self, datahandler: Callable[[str, bytes],None]):
        """Registers the data handler
        
        Args:
            datahandler (Callable[[bytes],None]): The data handler
        """

        raise NotImplementedError()

    async def on_connection(self, connection: _WrappedConnection):
        """Handles a new connection
        
        Args:
            connection (connwrapper._WrappedConnection): The connection to handle
        """

        raise NotImplementedError()