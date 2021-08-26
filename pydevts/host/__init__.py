"""
    Implements a basic TCP message host
"""
from ..logger import logger
from typing import Callable
from anyio import create_tcp_listener
from anyio.streams.tls import TLSListener
import ssl

class NodeHost:
    """
        Basic TCP message host
    """

    local_host: str
    local_port: int
    keypair: tuple[str, str]

    def __init__(self, local_host: str = None, local_port: int = None, keypair: tuple[str, str] = (None, None)):
        """[summary]

        Args:
            local_host (str, optional): IP address to host the server on. Defaults to None.
            local_port (int, optional): Port to host the server on. Defaults to None.
            keypair (tuple, optional): Tuple of PYCryptoDome public and private keys.. Defaults to (None, None).
        """

        # Validate local host
        if local_host is None:
            logger.debug("No host specified, using localhost")
            local_host = '127.0.0.1'
        
        # Validate local port
        if local_port is None:
            logger.debug('No port specified. Choosing random port')
            local_port = 0
        
        # Validate keypair
        if None in keypair:
            logger.warning('No keypair provided. The server will be unable to start in TLS mode.')
            keypair = (None, None)
        
        # Set values
        self.local_host = local_host
        self.local_port = local_port
        self.keypair = keypair

    @logger.catch
    def register_handler(self, handler):
        """
            Register a handler for the server
        """
        
        self.handlers.append(handler)
    
    @logger.catch
    async def _listen_handle(self, conn):
        print("Connection")

    @logger.catch
    async def run(self, tls: bool = False):
        """Start the server

        Args:
            tls (bool, optional): If we should start in TLS mode. Defaults to False.
        """

        # Verify we can use TLS
        if tls and None in self.keypair:
            raise RuntimeError("Unable to start in TLS mode. No valid keypair provided.")
        
        # Log that we are initializing the server
        logger.debug("Initializing server")

        # Create the server
        listener = create_tcp_listener(self.local_host, self.local_port)

        # Get the port
        port = listener.listeners[0]._raw_socket.getsockname()[1]

        # If we are using TLS, overwrite with TLS listener
        if tls:
            # Create ssl context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

            # Load the keypair
            context.load_cert_chain(certfile=self.keypair[0], keyfile=self.keypair[1])

            # Create TLS listener
            listener = TLSListener(listener, context=context)

        # Log that we are starting the server
        logger.info(f"Starting server on host {self.local_host}:{port}")

        # Start the server
        await listener.serve(self._listen_handle)