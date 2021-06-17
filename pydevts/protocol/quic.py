"""
    Basic QUIC protocol implementation
"""
from pydevts.protocol._base import *
import aioquic
import aioquic.quic
from aioquic.quic import events
import aioquic.quic.connection
import aioquic.quic.configuration
import anyio.abc._sockets
from contextlib import AsyncExitStack
import anyio
import uuid
import time
import socket

class QUICTransport(PYDEVTSTransport):
    """
        Base class for all transport protocols
    """
    address: AddressType
    _sock: anyio.abc._sockets.UDPSocket

    

    def __init__(self, address: AddressType):
        """
            Initiates transport object with address.
            The usage of this address will be determined by further methods called.
        """
        
        # Set address in self
        self.address = address

        # We are not active
        self.active = False

        # Create our task group as none
        self._tg = None

        # Initialize quic to none
        self._quic = None
        self._conf = None

        # This is our kill flag. If this is set
        # then tasks will start to shut down
        self._kill = False

        # Initialize our underlying socket to none
        self._sock = None

        # Timer
        self._timer_at = None
        self._timer = None

        # Create our exit stack
        self._es = AsyncExitStack()

        self._connection_terminated_handler = lambda: None
    
    async def serve(self, callback: CoroutineType):
        """
            This function creates a blocking server that binds to the address specified
            in the constructor of this class. Does not return and must be called asynchronously.
            When a connection is received, callback is executed.
        """
        ...
    async def _block(self):
        while not self._kill:
            await anyio.sleep(1)

    async def open(self) -> "PYDEVTSTransport":
        """
            This function opens a client that connects to a server at the address
            specified in the constructor of this class.
            As a convenience, this method returns self.
        """
        # Enter exit stack
        await self._es.__aenter__()

        # Create task group
        self._tg = await self._es.enter_async_context(anyio.create_task_group())

        # Create our socket
        self._sock = await self._es.enter_async_context(await anyio.create_udp_socket(family=socket.AF_INET))
        

        # Set quic configuration
        self._conf = aioquic.quic.configuration.QuicConfiguration(
            is_client = True, # We are connecting as a client
        )

        # Create quic connection
        self._quic = aioquic.quic.connection.QuicConnection(
            configuration=self._conf
        )

        # Connect
        self._quic.connect(self.address,time.time())

        # Initial transmit
        await self._transmit()


        
        # Mark self as active
        self.active = True

        # Return self
        return self
    
    

    async def close(self, exc_type: Optional[Type[BaseException]] = None,
            exc_val: Optional[BaseException] = None,
            exc_tcbk: Optional[TracebackType] = None):
        """
            This function closes the current client, or stops the current server.
        """

        # Close quic
        self._quic.close()

        # Transmit one last time
        await self._transmit()
        
        # Exit our exit stack
        await self._es.__aexit__(exc_type,exc_val,exc_tcbk)
        
        # Cleanup
        self._tg = None
        self._sock = None
        
        

        # Deactivate
        self.active = False

        # Reset kill flag
        self._kill = False

    async def __aenter__(self) -> "PYDEVTSTransport":
        """
            Context manager __aenter__ that wraps self.open
        """
        return await self.open()
    
    async def __aexit__(self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tcbk: Optional[TracebackType]):
        """
            Context manager __aexit__ that wraps self.close
        """

        await self.close()

    async def _transmit(self):
        """
            Sends datagrams and arms timer
        """
        

        # Send Datagrams
        for data, addr in self._quic.datagrams_to_send(
                time.time()):
            await self._sock.sendto(data,addr[0],addr[1])
        
        # Arm timer

        # Grab the new timer time
        timer = self._quic.get_timer()
        # If our timer is set and it is not the current timer
        if self._timer != None and self._timer_at != timer:
            self._timer = None
        if self._timer == None and timer != None:
            self._timer = await self._delay(timer, self._handle_timer)
        self._timer_at = timer
        
        

    async def _delay(self, wtime: float, func, *args, **kwargs):
        """
            Delays {func} execution until time {wtime}
        """
        name = uuid.uuid4()
        async def _func(task_status,*args,**kwargs):
            task_status.started()
            await anyio.sleep(wtime-time.time())
            await func(*args,**kwargs)
        await self._tg.start(_func, name=name)
        return name

    async def _handle_timer(self):
        """
            Internal function to handle timer
        """
        print("timer")
        self._timer = None
        self._timer_at = None
        self._quic.handle_timer(time.time())
        await self._process_events()
        await self._transmit()
    
    async def _process_events(self):
        event = self._quic.next_event()
        while event is not None:
            if isinstance(event, events.ConnectionTerminated):
                self._connection_terminated_handler()

            print(event)
            event = self._quic.next_event()

    async def send(self, data: bytes):
        """
            Sends a message consisting of {data}
        """
        self._quic.send_stream_data(
            self._quic.get_next_available_stream_id(),
            data
        )
        
        self._tg.start_soon(self._transmit)
        

        
    
    async def recv(self, size: Optional[int] = 0) -> bytes:
        """
            Receives a message of max size {size}
            If {size} is not provided, it will default to an implementation 
            specific value.
        """

        # Receive a datagram
        dg = await self._sock.receive()
        
        # Tell aioquic that we have received something
        self._quic.receive_datagram(dg[0],dg[1],time.time())
        
        # Transmit
        await self._transmit()
        
        return b""
