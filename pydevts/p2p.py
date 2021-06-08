import uuid
from anyio.streams.stapled import MultiListener
from anyio.abc._sockets import SocketStream
import anyio
from loguru import logger
from .conn import Connection
from .routers.basic import BasicRouter
from . import errors

class P2PConnection:
    """
        Connects to an individual client over
    """