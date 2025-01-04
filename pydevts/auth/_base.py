"""
    Base class for authentication formats
"""

# Type hints
from ..proto._base import _Conn

class _Auth:
    """
        Base class for authentication formats
    """

    def __init__(self):
        """Initialize the class"""
        
        raise NotImplementedError("This is an abstract class")

    async def handshake(self, conn: _Conn):
        """Execute the initial handshake for authentication
        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        raise NotImplementedError("This is an abstract class")
    
    async def accept_handshake(self, conn: _Conn):
        """The server side version of _Auth.handshake
        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        raise NotImplementedError("This is an abstract class")