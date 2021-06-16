"""
    QUIC socket implementation on top of anyio
"""
from pydevts.protocol._base import *
import aioquic.quic.connection
import aioquic.quic.configuration
import anyio
import anyio.to_process
import socket
import time

class QUICConnection(PYDEVTSConnection):
    """
        Represents a QUIC connection to a client or server
    """
    wrapped: aioquic.quic.connection.QuicConnection
    owner: "QUICTransport"
    async def connect(self, wraps: aioquic.quic.connection.QuicConnection, owner: "QUICTransport"):
        """
            Represents a QUIC connection to a client or server
        """

        # Save wrapped
        self.wrapped = wraps

        # Save owner
        self.owner = owner

        # Create datagram connection
        self.sock = await anyio.create_udp_socket(family=socket.AF_INET,
            local_host=0)
        
        # Timer event
        self.timer_event = anyio.Event()
        self.timer_for = time.time() + 5
        
        # Run handler
        await anyio.to_thread.run_sync(self._wait_sync,cancellable=True)
        print("hi")
        # QUIC connect
        self.wrapped.connect(
            (self.owner.host,self.owner.port,),
            time.time()
        )

        # Handle datagrams
        await self._handle_systems()
    
    def _wait_sync(self):
        while time.time() < self.timer_for:
            time.sleep(1)
        anyio.from_thread.run_async_from_thread(self.cont)

    async def _handle_systems(self):
        """
            Internal function to send datagrams
        """

        # Get datagrams to send
        to_send = self.wrapped.datagrams_to_send(time.time())
        
        # Send them
        for data,host in to_send:
            await self.sock.sendto(data,*host)
    
    

    async def send(self, data: bytes):
        """
            This method sends all of the data provided over the connection.
        """
        
        # Send
        self.wrapped.send_datagram_frame(data)

        t = self.wrapped.get_timer()
        
        # TODO This is 100% inefficient and should be fixed.
        if t != None:
            await anyio.sleep(t-time.time())
            self.wrapped.handle_timer(time.time())

        await self._handle_systems()

    async def recv(self, size: int) -> bytes:
        """
            This method receives {size} data.
        """
        
        # Receive datagrams
        data = await self.sock.receive()

        self.wrapped.receive_datagram(data[0],data[1],time.time())

        await self._handle_systems()

        

        
    
    async def close(self):
        """
            This method closes the connection
        """
        pass

class QUICTransport(PYDEVTSConnection):
    """
        Base class for all transport protocols
    """

    async def connect(self, host: str, port: int) -> "QUICConnection":
        """
            Connects to host:port and returns connection
        """
        
        # Store host and port
        self.host = host
        self.port = port

        # Create configuration
        self.conf = aioquic.quic.configuration.QuicConfiguration(
            is_client=True
        )

        # Create connection
        connection = aioquic.quic.connection.QuicConnection(
            configuration=self.conf
        )

        # Wrap
        conn = QUICConnection()
        await conn.connect(connection, self)

        # Return
        return conn

    async def serve(self, callback: CoroutineType, host: str, port: int = 0):
        """
            This method serves on the specified host and port. Used by servers
        """
        
        # Store host and port
        self.host = host
        self.port = port
    

