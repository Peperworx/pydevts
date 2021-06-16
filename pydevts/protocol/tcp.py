"""
    TCP socket implementation on top of anyio
"""
from pydevts.protocol._base import *
import anyio
from anyio.abc._sockets import SocketStream as AnyioSocketStream

class TCPConnection(PYDEVTSConnection):
    """
        Basic TCP connection implementation.
    """
    wrapped: AnyioSocketStream

    def __init__(self, wraps: AnyioSocketStream):
        """
            Basic TCP connection implementation.
        """
        # Set wrapped
        self.wrapped = wraps
    
    async def send(self, data: bytes):
        """
            This method sends all of the data provided over the connection.
        """
        # Pass through
        await self.wrapped.send(data)
    
    async def recv(self, size: int) -> bytes:
        """
            This method receives {size} data.
        """
        # Pass through
        return await self.wrapped.receive(size)
    
    async def close(self):
        """
            This method closes the connection
        """
        await self.wrapped.aclose()

class TCPTransport(PYDEVTSTransport):
    """
        Basic TCP transport implementation
    """

    async def connect(self, host: str, port: int = None) -> "TCPConnection":
        """
            Connects to host:port and returns connection
        """

        if port == None:
            raise TypeError("connect() missing 1 required argument: 'port'")
        
        
        # Anyio connect
        conn = await anyio.connect_tcp(host, port)

        # Create wrapper
        conn = TCPConnection(conn)

        # Return
        return conn
    
    async def serve(self, callback: CoroutineType, host: str, port: int = 0):
        """
            This method serves on the specified host and port. Used by servers
        """
        # Save callback
        self.callback = callback

        # Create listener
        self.listener = await anyio.create_tcp_listener(
            local_host=host,local_port=port
        )
        print(self.listener.listeners[0]._raw_socket.getsockname())
        # Serve
        await self.listener.serve(self._serve)
    
    async def _serve(self, conn):
        """
            Internal function to handle serve callback.
        """

        # Wrap connection
        conn = TCPConnection(conn)

        # Call callback
        await self.callback(conn)



