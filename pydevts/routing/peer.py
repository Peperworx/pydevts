"""
    Basic peer-based routing system
"""

# Logging
from ..logger import logger


# Unique IDs
import uuid

# Router parent
from ._base import _Router

# Type Hints
from ..proto import _Client, _Conn, _Server

# Clients and servers
from ..conn import MultiClientCache

# TCP server is default
from ..proto import TCPServer


class PeerRouter(_Router):
    """Peer-based routing system
    """

    entry_addr: tuple[str, int]
    host_addr: tuple[str, int]
    connections: MultiClientCache
    peers: dict[str, tuple[str, int]]

    def __init__(self):
        """Initialize the router
        """

        
        # Set default values
        self.peers = dict()
        self.data_handler = None

        # Create MultiConnectionCache
        self.connections = MultiClientCache()

    async def enter(self, entry_addr: tuple[str, int], host_addr: tuple[str, int]):
        """Enters a cluster

        Args:
            entry_addr (tuple[str, int]): The address of the entry node.
            host_addr (tuple[str, int]): The address that we are hosting on
        """

        # Save entry address and host address
        self.entry_addr = entry_addr
        self.host_addr = host_addr

        

        raise NotImplementedError("This is an abstract class")
    
    async def send_to(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        raise NotImplementedError("This is an abstract class")
    
    async def emit(self, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            data (bytes): The data to emit
        """

        raise NotImplementedError("This is an abstract class")
    
    async def register_data_handler(self, data_handler: Callable[[bytes],None]):
        """Registers the data handler
        
        Args:
            data_handler (Callable[[bytes],None]): The handler which is called when data is received.
        """

        raise NotImplementedError("This is an abstract class")

    async def on_connection(self, connection: _Conn):
        """Handles a new connection
        
        Args:
            connection (_Conn): The connection to handle
        """

        raise NotImplementedError("This is an abstract class")