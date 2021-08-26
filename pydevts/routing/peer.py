"""
    Basic peer-based routing system
"""

# Router parent
from ._base import _Router

# Type Hints
from ..connwrapper import _WrappedConnection
from typing import Callable


class PeerRouter(_Router):
    """Peer-based routing system
    """

    keypair: tuple[str, str]

    def __init__(self, keypair: tuple[str, str] = (None, None)):
        """Initialize the router

        Args:
            keypair (tuple[str, str], optional): The public-private keypair to use for encryption. Defaults to (None, None).
        """

        self.keypair = keypair
    
    async def enter(self, host: str, port: int, tls: bool = False):
        """Enters a cluster

        Args:
            host (str): The entry host of the cluster
            port (int): The entry port of the cluster
            tls (bool, optional): Whether to use TLS. Defaults to False.
        """

        raise NotImplementedError()
    
    async def sendto(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        raise NotImplementedError()
    
    async def on_connection(self, connection: _WrappedConnection, datahandler: Callable[[bytes],None]):
        """Handles a new connection
        
        Args:
            connection (connwrapper._WrappedConnection): The connection to handle
        """

        raise NotImplementedError()

