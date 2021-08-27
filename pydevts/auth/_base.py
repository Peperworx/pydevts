"""
    Base class for authentication formats
"""

# Type hints
from ..connwrapper import _WrappedConnection

class _Auth:
    """
        Base class for authentication formats
    """

    def __init__(self):
        """Initialize the class"""
        
        raise NotImplementedError("This is an abstract class")

    async def handshake(self, conn: _WrappedConnection):
        """Execute the initial handshake for authentication

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        raise NotImplementedError("This is an abstract class")
    
    async def accept_handshake(self, conn: _WrappedConnection):
        """The server side version of _Auth.handshake

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        raise NotImplementedError("This is an abstract class")
    
