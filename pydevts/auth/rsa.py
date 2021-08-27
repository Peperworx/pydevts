"""
    RSA key based authentication
"""

# Type hints
from ..connwrapper import _WrappedConnection

# Base class
from ._base import _Auth

class AuthRSA(_Auth):
    """
        Authentication method which does... Nothing.
    """

    def __init__(self):
        """Initialize the class"""
        
        pass

    async def handshake(self, conn: _WrappedConnection):
        """Execute the initial handshake for authentication

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        pass
    
    async def accept_handshake(self, conn: _WrappedConnection):
        """The server side version of _Auth.handshake

        Args:
            conn (_WrappedConnection): The connection that we are using
        """

        pass
    
