"""
    Public node interface that wraps around P2PConnection
"""

# Type hints
from typing import Callable
from anyio.abc import TaskStatus

# Serialization
from .msg import MsgName

# P2P Connection
from .p2p import P2PConnection

# Errors
from .err import EventNotFound

# Anyio stuff
from anyio import create_task_group, TASK_STATUS_IGNORED

# Logging
from .logger import logger

class Node(P2PConnection):
    """A peer to peer node with event handling
    """


    _events: dict[str, list[Callable[[str, bytes], None]]]
    _syst_events: dict[str, list[Callable[[], None]]]

    def __init__(self, *args, **kwargs):
        
        # Initialize events
        self._events = dict()

        # Initialize system events
        self._syst_events = {
            "startup": [self._startup]
        }

        # Call super
        super().__init__(*args, **kwargs)

    async def _startup(self):
        """Startup event
        """

        logger.info(f"Runing server at {self.router.node_id}@{self.addr[0]}:{self.addr[1]}")
    
    async def _call_sys(self, name: str):
        """Call a system event

        Args:
            name (str): The name of the event to call.
        """

        # If the event does not exist, raise an error
        if name not in self._syst_events.keys():
            raise EventNotFound(f"Event {name} not found")

        # Run the events
        for func in self._syst_events[name]:
            await func()

    async def run(self, task_status: TaskStatus = TASK_STATUS_IGNORED):
        """Start running the server
        """
        # Create a task group
        async with create_task_group() as tg:
            # Start the server
            await tg.start(self.server.run)

            # Run the startup events
            await self._call_sys("startup")

            # Signal ready
            task_status.started()
            
    def on_sys(self, name: str):
        """Decorator to register a system event handler

        Args:
            name (str): The name of the event to register.
        """

        # Create the event if it does not exist
        if name not in self._syst_events.keys():
            self._syst_events[name] = []

        def _deco(func) -> Callable[[str, bytes], None]:
            """Decorator to register an event handler
            """

            # Register the handler
            self._syst_events[name].append(func)

            # Return the function
            return func
        
        return _deco  

    def on(self, name: str):
        """Decorator to register an event handler

        Args:
            name (str): The name of the event to register.
        """

        def _deco(func) -> Callable[[str, bytes], None]:
            """Decorator to register an event handler
            """

            # Register the handler
            self._on(name, func)

            # Return the function
            return func
        
        return _deco

    def _on(self, name: str, handler: Callable[[str, bytes], None]):
        """Register an event handler for an event

        Args:
            name (str): Name of the event to register.
            handler (Callable[[str, bytes], None]): The event handler.
        """
    
        # If the event does not exist, create it
        if name not in self._events.keys():
            self._events[name] = []

        # Set the handler
        self._events[name].append(handler)

    async def _on_data(self, node: str, data: bytes):
        """Handle data received

        Args:
            data (bytes): The data received.
        """

        # Deserialize the data
        name, sent_data = MsgName.loads(data)

        # Send to registered handlers
        if name in self._events.keys():
            for handler in self._events[name]:
                await handler(node, sent_data)
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
    
    async def send(self, node: str, name: str, data: bytes):
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
