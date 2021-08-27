"""
    Public interface for pydevts
"""

# Type hints
from typing import Callable
from .auth._base import _Auth


# Wraps this
from .node import _Node

# Auth
from .auth.noauth import AuthNone

# Anyio
from anyio import create_task_group


class Node:
    """
        A PYDEVTS Node.
    """

    _node: _Node
    _events: dict[str, list[Callable[[str, str, bytes],None]]]
    _sys_events: dict[str, list[Callable[[], None]]]


    def __init__(self, entry_addr: tuple[str, int], host_addr: tuple[str, int] = ("0.0.0.0", 0), auth_method: _Auth = AuthNone()):
        """Initialize the node

        Args:
            entry_addr (tuple[str, int]): The address of the entry node
            auth_method (Auth, optional): The authentication method to use
        """
        
        # Create wrapped node
        self._node = _Node(entry_addr, host_addr=host_addr, auth_method=auth_method)

        # Initialize event handlers
        self._events = dict()
        self._sys_events = {
            "startup":[],
        }

        

    def on(self, event: str):
        """Decorator frontend for adding event handlers

        Args:
            event (str): [description]
        """

        def decorator(func: Callable[[str, str, bytes], None]):
            # Delegate to node
            self._node.bind(event, func)
            return func

        return decorator


    def on_sys(self, event: str):
        """Decorator frontend for adding system event handlers

        Args:
            event (str): [description]
        """

        def decorator(func):
            if event not in self._sys_events.keys():
                raise AttributeError(f"No such system event: {event}")
            self._sys_events[event].append(func)
            return func

        return decorator
    
    async def emit(self, event: str, data: bytes):
        """Emit an event

        Args:
            event (str): The event to emit
            data (bytes): The data to send
        """

        # Delegate to _node
        await self._node.emit(event, data)
    
    async def send(self, node: str, name: str, data: bytes):
        """Send data to a node
        
        Args:
            node (str): The node to send to
            name (str): The name of the event
            data (bytes): The data to send
        """

        # Delegate to _node
        await self._node.send(node, name, data)
    
    
    async def run(self, verify_key: str = None):
        """Run the node

        Args:
            verify_key (str, optional): This verify key is the path to the private key of a serve which should be used in TLS mode.
                This will be removed in future versions as we implement our own encryption.
        """

        # Create task group
        async with create_task_group() as tg:
            await tg.start(self._node.run, verify_key)
            
            # Run system events
            for event in self._sys_events["startup"]:
                await event()