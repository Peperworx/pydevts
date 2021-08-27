"""Implements system for MultiPeer P2P connections
"""

# Routers
from .routing.peer import PeerRouter

# Type Hints
from .connwrapper import _WrappedConnection

from .routing._base import _Router
from typing import Callable
from .auth._base import _Auth

# Node hosts and connections
from .host import NodeHost
from .conn import NodeConnection

# Authentication
from .auth.noauth import AuthNone

# Synchronization
from anyio import Condition


class P2PConnection:
    """Peer to peer data passing
    """

    host: str
    port: int
    entry_host: str
    entry_port: int
    router: _Router
    server: NodeHost
    handler: Callable[[_WrappedConnection], None]
    data_handler: list[Callable[[str, bytes], None]]
    auth_method: _Auth

    def __init__(self, host: str = "0.0.0.0", port: int = 0,
        router: _Router = PeerRouter,
        auth_method: _Auth = AuthNone()):
        """Initialize P2PConnection

        Args:
            host (str): The hostname to host on
            port (int, optional): The port to host on. Defaults to 0.
            auth_method (_Auth): The authentication method to be used
        """

        # Save host and port
        self.host = host
        self.port = port

        # Save auth method
        self.auth_method = auth_method

        # Initialize router
        self.router = router()

        # Data handler
        self.data_handler = []
    
    async def connect(self, host: str, port: int):
        """Connect to a remote host
        
        Args:
            host (str): The hostname to connect to
            port (int): The port to connect to
        """
        
        # Set up saved values
        self.entry_host = host
        self.entry_port = port
    
        # Create the host
        self.server = NodeHost(self.host, self.port, auth_method=self.auth_method)

        # Prepare the host
        await self.server.init(self.router.on_connection)

        # Register the data handler
        await self.router.register_handler(self.on_data)

        # Tell router to enter the network
        await self.router.enter(host, port, (self.server.local_host, self.server.local_port),
            auth_method=self.auth_method)

    async def run(self):
        """Start running the server
        """

        # Start the server
        await self.server.run()
    
    async def on_data(self, node: str, data: bytes):
        """Called when data is received

        Args:
            node (str): The node that sent the data
            data (bytes): The data received
        """

        # Delegate to registered handler
        for handler in self.data_handler:
            await handler(node, data)

    def register_data_handler(self, handler: Callable[[str, bytes], None]):
        """Register a handler for data received

        Args:
            handler (Callable[[bytes], None]): The handler to register
        """

        # Set the handler
        self.data_handler.append(handler)

    async def send_to(self, node: str, data: bytes):
        """Send data to node

        Args:
            node (str): The node to send data to
            data (bytes): The data to send
        """

        # Delegate to router
        await self.router.send_to(node, data)
    
    
    async def emit(self, data: bytes):
        """Sends data to all nodes in the network

        Args:
            data (bytes): The data to send
        """

        # Delegate to router
        await self.router.emit(data)


        
        

    