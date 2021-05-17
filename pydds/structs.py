"""
    Contains the base data structures that PYDDS uses
"""


import pydantic
from enum import Enum


class EEventType(Enum):
    """
        Enumeration of the event types
    """
    REP_SERVER = 0 # Executes on all nodes
    REP_CLIENTS = 1 # Executes on all clients
    REP_MULTICAST = 2 # Executes on all nodes and clients
    REP_FINDONE = 3 # NOT IMPLEMENTED: Finds a node to execute on based off of a provided function


class EventDispatch(pydantic.BaseModel):
    data: bytes
    name: str
    type: int