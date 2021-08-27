"""
    Implements a basic TCP message host
"""
# Logging
from ..logger import logger

# Type hints
from typing import Callable, Optional
from ..auth._base import _Auth

# Errors
from ..auth import AuthenticationError

# Anyio
import anyio

# Encryption
from anyio.streams.tls import TLSListener
import ssl
from ..auth.noauth import AuthNone

# Wrapped connection
from ..connwrapper import _WrappedConnection



class NodeHost:
    """
        Basic TCP message host
    """

    local_host: str
    local_port: int
    ssl_context: Optional[ssl.SSLContext]
    handler: Callable[[_WrappedConnection], None]
    auth_method: Optional[_Auth]

    def __init__(self, local_host: str = None, local_port: int = None, ssl_context: ssl.SSLContext = None, auth_method: _Auth = AuthNone()):
        """[summary]

        Args:
            local_host (str, optional): IP address to host the server on. Defaults to None.
            local_port (int, optional): Port to host the server on. Defaults to None.
            ssl_context (ssl.SSLContext, optional): SSL context to use for TLS. Defaults to None.
        """

        # Validate local host
        if local_host is None:
            logger.debug("No host specified, using localhost")
            local_host = '127.0.0.1'
        
        # Validate local port
        if local_port is None:
            logger.debug('No port specified. Choosing random port')
            local_port = 0
        
        # Validate ssl context
        if ssl_context == None:
            logger.warning('No ssl context provided. The server will be unable to start in TLS mode.')
        
        # Set values
        self.local_host = local_host
        self.local_port = local_port
        self.ssl_context = ssl_context

        # Set authentication method
        self.auth_method = auth_method

    
    
    async def _listen_handle(self, conn):
        

        # Wrap the connection
        connection = _WrappedConnection(conn)

        
        try:
            # Run authentication
            if self.auth_method:
                await self.auth_method.accept_handshake(connection)

            # Call the handler
            await self.handler(connection)
        except (anyio.EndOfStream, ConnectionError, AuthenticationError):
            pass

        # Close the connection
        await connection.close()

    async def init(self, handler: Callable[[_WrappedConnection], None], tls: bool = True):
        """Initialize the server

        Args:
            handler (Callable[[Any], None]): Handler to call when a connection is made
            tls (bool, optional): Whether to use TLS. Defaults to True.
        """

        # Set the handler
        self.handler = handler

        # Verify we can use TLS
        if tls and self.ssl_context == None:
            raise RuntimeError("Unable to start in TLS mode. No valid ssl context provided.")
        
        # Log that we are initializing the server
        logger.debug("Initializing server")

        # Create the server
        self.listener = await anyio.create_tcp_listener(local_host=self.local_host, local_port=self.local_port)

        # Get the port
        self.local_port = self.listener.listeners[0]._raw_socket.getsockname()[1]

        # If we are using TLS, overwrite with TLS listener
        if tls:
            # Create TLS listener
            self.listener = TLSListener(self.listener, self.ssl_context)
        
        # Log that we have initialized the server
        logger.info(f"Initialized server at {self.local_host}:{self.local_port}")
    
    async def run(self):
        """Start the server
        """

        logger.info(f"Starting server.")

        # Start the server
        await self.listener.serve(self._listen_handle)