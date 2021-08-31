"""
    Event wrapper around P2PConnections
"""

# P2P Connection
from .p2p import P2PConnection

# Serialization
from .msg import MsgName

# Type hints
from typing import Callable

# Errors
from .err import EventNotFound

class P2PEventSystem(P2PConnection):
    """
        Event system for P2P connections
    """

    data_handlers: list[Callable[[str, str, bytes], None]]
    event_handlers: dict[str, Callable[[str, bytes], None]]

    def __init__(self, *args, **kwargs):
        
        self.event_handlers = dict()
        self.data_handlers = []

        # Call super
        super().__init__(*args, **kwargs)


    def register_event_handler(self, name: str, handler: Callable[[str, bytes], None]):
        """Register the event handler for an event

        Args:
            name (str): Name of the event to register.
            handler (Callable[[str, bytes], None]): The event handler.
        """
    
        
        # Just set the handler
        self.event_handlers[name] = handler

    async def _on_data(self, node: str, data: bytes):
        """Handle data received

        Args:
            data (bytes): The data received.
        """

        # Deserialize the data
        name, sent_data = MsgName.loads(data)

        # Send to registered handler
        if name in self.event_handlers.keys():
            await self.event_handlers[name](node, sent_data)
        else:
            raise EventNotFound(f"Event {name} not found")
    
    async def emit(self, name: str, data: bytes):
        """Send event to all peers

        Args:
            name (str): The name of the event to send.
            data (bytes): The data to send.
        """

        # Serialize the data
        send_data = MsgName.dumps(name, data)

        # Delegate to the underlying P2PConnection
        await super().emit(send_data)
    
    async def send_to(self, node: str, name: str, data: bytes):
        """Send event to a specific node

        Args:
            node (str): The node to send the data to.
            name (str): The name of the evemt to send.
            data (bytes): The data to send.
        """

        # Serialize the data
        send_data = MsgName.dumps(name, data)

        # Delegate to the underlying P2PConnection
        await super().send_to(node, send_data)
