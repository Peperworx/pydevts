"""
    Simple wrapper around anyio TCP.
"""
import anyio
from anyio._core._sockets import SocketStream
from pydevts.protocol._base import *

class TCPTransport(PYDEVTSTransport):
    """
        Base class for all transport protocols
    """
    address: AddressType
    wrapped: SocketStream
    listener: SocketStream
    

    def __init__(self, address: AddressType):
        """
            Initiates transport object with address.
            The usage of this address will be determined by further methods called.
        """
        
        # Set address in self
        self.address = address

        self.wrapped = None
        self.listener = None

        
    
    async def _wrap(self, wraps):
        """
            Wraps a SocketStream.
        """
        self.wrapped = wraps
    
    async def serve(self, callback: CoroutineType):
        """
            This function creates a blocking server that binds to the address specified
            in the constructor of this class. Does not return and must be called asynchronously.
            When a connection is received, callback is executed.
        """
        
        # Create listener
        self.listener = await anyio.create_tcp_listener(
            local_host = self.address[0],
            local_port = self.address[1],
        )
        print(self.listener.listeners[0]._raw_socket.getsockname())

        # Serve function that wraps the SocketStream in a new TCPTransport
        #  object
        async def _serve(conn: SocketStream):
            new_conn = TCPTransport(conn._raw_socket.getsockname())
            await new_conn._wrap(conn)
            await callback(new_conn)


        # Serve
        await self.listener.serve(_serve)


    async def open(self) -> "PYDEVTSTransport":
        """
            This function opens a client that connects to a server at the address
            specified in the constructor of this class.
            As a convenience, this method returns self.
        """

        # Set listener to none
        self.listener = None

        # Create connection
        self.wrapped = await anyio.connect_tcp(
            self.address[0], self.address[1]
        )

        # Return self
        return self
    
    async def close(self):
        """
            This function closes the current client, or stops the current server.
        """
        
        # If it is a listener, close it
        if self.listener:
            await self.listener.aclose()
        
        # If it is wrapped, close the wrapped
        if self.wrapped:
            await self.wrapped.aclose()

        # Clear each
        self.wrapped = None
        self.listener = None



    async def __aenter__(self) -> "PYDEVTSTransport":
        """
            Context manager __aopen__ that wraps self.open
        """

        return await self.open()
    

    async def __aexit__(self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tcbk: Optional[TracebackType]):
        """
            Context manager __aclose__ that wraps self.close
        """

        await self.close()


    
    async def send(self, data: bytes):
        """
            Sends a message consisting of {data}
        """

        # Send from the wrapped object
        await self.wrapped.send(data)
    
    async def recv(self, size: Optional[int] = 65536) -> bytes:
        """
            Receives a message of max size {size}
            If {size} is not provided, it will default to an implementation 
            specific value.
        """

        # Receive from the wrapped object
        return await self.wrapped.receive(size)
