"""Implements system for MultiPeer P2P Connections
"""

# Logging
from .logger import logger

# Anyio
from anyio import create_task_group

# Routers
from .routing import PeerRouter

# Type hints
from .proto._base import _Conn, _Client, _Server
from .routing._base import _Router
from typing import Callable
from .auth._base import _Auth

# Default server is TCP
from .proto import TCPProto

# Default authentication is no auth
from .auth import AuthNone

class P2PConnection:
    """Multipeer P2P communications
    """

    addr: tuple[str, int]
    entry_addr: tuple[str, int]

    router: _Router

    server: _Server

    handler: Callable[[_Conn], None]
    data_handler: list[Callable[[str, bytes], None]]
    auth: _Auth

    def __init__(self, host: str = "0.0.0.0",
        port: int = 0,
        router: _Router = PeerRouter,
        protocol: tuple[_Client, _Conn, _Server] = TCPProto,
        auth_method: _Auth = AuthNone()):
        """Initialize P2PConnection

        Args:
            host (str, optional): The host to listen on. Defaults to "0.0.0.0".
            port (int, optional): The port to listen on. Defaults to 0.
            router (_Router, optional): The router to use. Defaults to PeerRouter.
            auth_method (_Auth, optional): The authentication method to use. Defaults to AuthNone().
        """

        # Save host and port
        self.addr = (host, port)

        # Save auth method
        self.auth = auth_method

        # Initialize router
        self.router = router(protocol)

        # Initialize server
        self.server = protocol[2](host, port, self.router.on_connection)

        # Setup data handler
        self.data_handler = []
    
    async def connect(self, host: str, port: int):
        """Connect to cluster

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
        """

        # Save the entry address
        self.entry_addr = (host, port)

        # Register the data handler
        await self.router.register_data_handler(self._on_data)

        # Tell the router to enter the network
        await self.router.enter(
            self.entry_addr,
            self.addr
        )
    
    async def run(self, *args, **kwargs):
        """Start running the server
        """
        
        # Delegate to the server
        await self.server.run(*args, **kwargs)
        
        
    async def _on_data(self, node: str, data: bytes):
        """Handle data received

        Args:
            data (bytes): The data received.
        """

        # Delegate to registered handlers
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