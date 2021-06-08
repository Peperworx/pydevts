import uuid
from anyio.streams.stapled import MultiListener
from anyio.abc._sockets import SocketStream
import anyio
from loguru import logger
from .conn import Connection
from .routers.basic import BasicRouter
from . import errors

class P2PNode:
    """
        
    """

    nid: str # The node ID of this node
    listen_port: int # The port we are listening on
    server: MultiListener # The anyio listener

    def __init__(self):
        """
            A peer to peer node that spins up a local server and attempts to connect to cluster.
        """

        # Generate node ID
        self.nid = str(uuid.uuid4())

        # Initialize router
        self.router = BasicRouter(self)
    
    async def join(self, host: str, port: int):
        """
            Join a cluster using entry node
            Arguments
            - {host}
                The host of the entry node
            - {port}
                The port of the entry node
        """

        # Initialize local server
        await self._initialize()

        # Attempt to connect over router
        self.router.connect_to(host, port)
        

    async def start(self):
        """
            Starts the server with an empty cluster
        """

        # Initialize local server
        await self._initialize()
    
    async def _initialize(self):
        """
            Internal function that initializes a local TCP server for listening for p2p requests.
        """

        # Create listeners
        self.server = await anyio.create_tcp_listener(
            local_host = "0.0.0.0", # Every address
            local_port = 0 # Automaticaly choose a port
        )

        # Retreive the listen port of the first listener
        self.listen_port = self.server.listeners[0]._raw_socket.getsockname()[1]

        # Log that we are online
        logger.debug(f"Created listener at host 0.0.0.0:{self.listen_port}")
    
    async def run(self):
        """
            Begins execution of the server.
        """

        # Start serving
        await self.server.serve(self._pre_serve)
    
    async def _pre_serve(self, ss: SocketStream):
        """
            Internal function that proxies a connection handler to the _serve function
        """

        # Create connection instance
        conn = Connection(ss)

        # Call actual serve function
        await self._serve(conn)
    
    @errors.catch_all_continue
    async def _serve(self, conn: Connection):
        """
            Internal handler for TCP connections.
        """

        logger.info(f"Connection from {conn.host}:{conn.port}")

        try:
            while True:
                # Receive data
                data = await conn.recv()

                # Pass to router
                await self.router.receive(data)
        except anyio.EndOfStream:
            # Ignore EndOfStream
            logger.debug(f"{conn.host}:{conn.port} disconnected")
