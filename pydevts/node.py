"""Implements basic peer to peer node for messaging"""

import anyio

# The underlying connection
from pydevts.p2p import P2PConnection

# Type hints
from ssl import SSLContext
from typing import Callable
from .auth._base import _Auth

# Authentication
from .auth.noauth import AuthNone

class _Node:
    """Basic peer to peer node for messaging"""
    
    entry_addr: tuple[str, int]
    ssl_context: SSLContext
    on_start: list[Callable[[],None]]
    auth_method: _Auth

    def __init__(self, entry_addr: tuple[str, int], ssl_context: SSLContext = None, auth_method: _Auth = AuthNone()):
        """Basic peer to peer node for messaging

        Args:
            entry_addr (tuple[str, int]): The entry node in the cluster
            ssl_context (SSLContext): The ssl context used
            auth_method (_Auth): The authentication method to be used
        """

        # Save these for later
        self.entry_addr = entry_addr
        self.ssl_context = ssl_context
        self.auth_method = auth_method

        # Create the connection
        self.conn = P2PConnection(ssl_context = self.ssl_context, auth_method=auth_method)

        # Initialize events
        self.on_start = []
    async def run(self, verify_key: str = None):
        """Begins running the node
        
        Args:
            verify_key (str): Pass this if you are testing with another non-trusted private key.
        """
    
        # Connect to the entry node
        await self.conn.connect(*self.entry_addr, self.ssl_context != None, verify_key=verify_key)
        
        # Create anyio task group
        async with anyio.create_task_group() as tg:
            # Run the server
            tg.start_soon(self.conn.run)

            # Call all start events
            for handler in self.on_start:
                tg.start_soon(handler)
    
    def bind_start(self, handler: Callable[[], None]):
        """Binds the start event to the handler

        Args:
            handler (Callable[[], None]): The handler to call
        """

        self.on_start.append(handler)