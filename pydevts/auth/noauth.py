"""
    Auth method which does nothing.
"""

# Type hints
from ..proto._base import _Conn

class AuthNone:
    """
        Base class for authentication formats
    """

    def __init__(self):
        """Initialize the class"""
        
        pass

    async def handshake(self, conn: _Conn):
        """Execute the initial handshake for authentication
        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        pass
    
    async def accept_handshake(self, conn: _Conn):
        """The server side version of _Auth.handshake
        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        pass