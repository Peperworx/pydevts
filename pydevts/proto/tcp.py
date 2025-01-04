"""
    Wrapper classes over the anyio TCP implementation.
"""


# Base Classes
from ._base import _Conn, _Client, _Server


# Anyio TCP
from anyio import connect_tcp, create_tcp_listener, TASK_STATUS_IGNORED, EndOfStream
from anyio.abc import TaskStatus, SocketStream
from anyio.streams.stapled import MultiListener

# Type hints
from typing import Callable



class TCPConn(_Conn):
    """
        TCP connection wrapper.
    """

    _wraps: SocketStream

    # The address on the other end of the pipe
    addr: tuple[str, int]

    def __init__(self, wraps: SocketStream):
        """Initialize the wrapper class

        Args:
            wraps (SocketStream): The SocketStream to wrap
        """

        # Save the wrapped object
        self._wraps = wraps

        # Save the address
        self.addr = self._wraps._raw_socket.getpeername()
    
    async def recv(self, max_bytes: int = 35536) -> bytes:
        """Receive data overthe connection.

        Args:
            max_bytes (int, optional): Maximum number of bytes to receive. Defaults to 35536.

        Returns:
            bytes: Data received over the connection.
        """

        return await self._wraps.receive(max_bytes)
    
    async def send(self, data: bytes):
        """Send data over the connection.

        Args:
            data (bytes): Data to send.
        """

        await self._wraps.send(data)
    
    async def close(self):
        """Close the connection
        """

        await self._wraps.aclose()


class TCPClient(TCPConn, _Client):
    """
        TCP client wrapper.
    """

    

    @classmethod
    async def connect(cls, host: str, port: int) -> 'TCPClient':
        """Connects to a TCP server.

            Arguments:
                host (str): The host to connect to.
                port (int): The port to connect to.

            Returns:
                TCPClient: An instance of TCPClient for the connection.
        """
        
        # Connect to the server using anyio
        sock = await connect_tcp(host, port)

        # Create client
        return cls(sock)

class TCPServer(_Server):
    """
        TCP server wrapper.
    """

    _host: str
    _port: int
    port: int # The actual listening port
    _handler: Callable[[_Conn], None]
    _listener: MultiListener[SocketStream]

    def __init__(self, host: str, port: int, handler: Callable[[_Conn], None]):
        """[summary]

        Args:
            host (str): The host to listen on
            port (int): The port to listen on
            handler (Callable[[_Conn], None]): The connection handler
        """

        # Save host
        self._host = host

        # Save port
        self._port = port

        # Also save the public port
        self.port = port

        # Save handler
        self.handler = handler
    
    async def _wrap_handler(self, conn: SocketStream):
        """The connection handler

        Args:
            conn (SocketStream): Anyio SocketStream communicating with the client.
        """

        # Create the wrapper class
        new_conn = TCPConn(conn)

        # Try-except for disconnect
        try:
            # Run the handler
            await self.handler(new_conn)
        except (EndOfStream):
            # Connection closed
            return
        
        # Close the connection
        await new_conn.close()
            
    async def initialize(self):
        """Initialize the server.
        """

        # Create listener
        self._listener = await create_tcp_listener(local_host = self._host, 
            local_port = self._port)

        # Fetch listen port
        port = self._listener.listeners[0]._raw_socket.getsockname()[1]

        # Update public port value
        self.port = port

    async def run(self, task_status: TaskStatus = TASK_STATUS_IGNORED):
        """Run the server.

        Args:
            ONLY PASSED BY ANYIO:
            task (TaskStatus, optional, anyio): The task status. Defaults to TASK_STATUS_IGNORED.
        """

        # Initialize the server if it has not already
        # been initialized
        if not self._listener:
            await self.initialize()        

        # Task status ready (return our port)
        task_status.started(self.port)

        # Start listening
        await self._listener.serve(self._wrap_handler)