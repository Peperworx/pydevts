import uuid
from anyio.streams.stapled import MultiListener
from anyio.abc._sockets import SocketStream
import anyio
from loguru import logger
from .conn import Connection
from .routers.basic import EKERouter
from . import errors

class P2PNode:
    """
        A basic peer to peer node.
    """

    
    nid: str # The node ID of this node
    server: MultiListener # The anyio server listener
    listen_port: int # The port to listen on
    router: EKERouter

    def __init__(self):
        """
            A basic multi peer peer to peer node.
        """
        self.nid = str(uuid.uuid4())
        self.router = EKERouter(self)

    async def join(self,host: str,port: int):
        """
            Join a cluster.
        """

        # Initialize local server
        await self._initialize()


        await self.router.connect_to(host, port)

        await self.run()


    async def start(self):
        """
            Start a cluster
        """

        # Initialize local server
        await self._initialize()

        # That is all we need to do to start an empty cluster! Cool!


    async def _initialize(self):
        """
            Internal function to initialize peer to peer functionalities.
            Sets up a local server.
        """

        # Create listeners
        self.server = await anyio.create_tcp_listener(
            local_host="0.0.0.0", # All Ips
            local_port=0 # Choose a port
        )

        # Our listen port
        self.listen_port = self.server.listeners[0]._raw_socket.getsockname()[1]


        # Log
        logger.debug(f"Created listener at host 0.0.0.0:{self.listen_port}")



    async def run(self):
        """
            Begin executing server.
        """

        # Start serving
        await self.server.serve(self._serve)

    @errors.catch_all_continue
    async def _serve(self, ss: SocketStream):
        """
            Handler called on each request
        """

        # Wrap the connection
        conn = Connection(ss)

        

        logger.debug(f"Connection from {conn.host}:{conn.port}")

        try:
            # Loop until we fail
            while True:
                
                data = await self.router.receive(conn)
                print(data)

        except anyio.EndOfStream:
            # Ignore EndOfStream
            logger.debug(f"{conn.host}:{conn.port} disconnected")