"""Implements basic peer to peer node for messaging"""

import anyio


# The underlying connection
from pydevts.p2p import P2PConnection

# Type hints
from typing import Callable
from .auth._base import _Auth
import anyio.abc

# Authentication
from .auth.noauth import AuthNone

# Serialization
import msgpack

class _Node:
    """Basic peer to peer node for messaging"""
    
    entry_addr: tuple[str, int]
    on_start: list[Callable[[],None]]
    auth_method: _Auth
    _events: dict[str, Callable[[bytes], None]]

    def __init__(self, entry_addr: tuple[str, int], host_addr: tuple[str, int] = ("0.0.0.0", 0), 
        auth_method: _Auth = AuthNone()):
        """Basic peer to peer node for messaging

        Args:
            entry_addr (tuple[str, int]): The entry node in the cluster
            auth_method (_Auth): The authentication method to be used
        """

        # Save these for later
        self.entry_addr = entry_addr
        self.auth_method = auth_method

        # Create the connection
        self.conn = P2PConnection(host = host_addr[0], port = host_addr[1], 
            auth_method=auth_method)

        # Bind event handlers
        self.conn.register_data_handler(self._on_data)

        # Initialize events
        self.on_start = []
        self._events = dict()
    
    async def run(self, task_status: anyio.abc.TaskStatus = anyio.TASK_STATUS_IGNORED):
        """Begins running the node
        """
    
        # Connect to the entry node
        await self.conn.connect(*self.entry_addr)
        
        # Trigger task status
        task_status.started()

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
    
    def bind(self, name: str, handler: Callable[[str, str, bytes], None]):
        """Binds handler to an event name

        Args:
            name (str): The event name to bind the handler to
            handler (Callable[[bytes], None]): the handler function
        """

        # If we have no events of this name, create a new list
        if name not in self._events.keys():
            self._events[name] = []
        
        # Add the handler
        self._events[name].append(handler)
    
    async def _on_data(self, node: str, data: bytes):
        """Called when data is received

        Args:
            node (str): The node that send the event
            data (bytes): The data received
        """

        # Unpack the data
        name, data = msgpack.unpackb(data)

        # If we have no events of this name, just return
        if name not in self._events.keys():
            return

        # Call all handlers
        for handler in self._events[name]:
            await handler(node, name, data)
    
    async def send(self, node_id: str, name: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The node id to send to
            name (str): The event name to send
            data (bytes): The data to send
        """

        # Delegate to connection
        await self.conn.send_to(node_id, msgpack.packb((name, data)))
    
    async def emit(self, name: str, data: bytes):
        """Emits an event

        Args:
            name (str): The event name to emit
            data (bytes): The data to send
        """

        # Delegate to connection
        await self.conn.emit(msgpack.packb((name, data)))