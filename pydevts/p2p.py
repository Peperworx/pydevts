import uuid
from anyio.streams.stapled import MultiListener
from anyio.abc._sockets import SocketStream
import anyio
from loguru import logger
from .conn import Connection
from .routers.hopbased import HopBasedRouter
from . import errors
import msgpack
from types import FunctionType

class P2PNode:
    """
        A basic peer to peer node.
    """

    
    nid: str # The node ID of this node
    server: MultiListener # The anyio server listener
    listen_port: int # The port to listen on
    router: HopBasedRouter
    callbacks: dict[str, list[FunctionType]]
    entry: dict # The entry node

    def __init__(self):
        """
            A basic multi peer peer to peer node.
        """
        self.nid = str(uuid.uuid4())
        self.router = HopBasedRouter(self)
        self.callbacks = {}

    async def join(self,host: str,port: int):
        """
            Join a cluster.
        """

        # Initialize local server
        await self._initialize()


        entry = (await self.router.connect_to(host, port))

        if entry == None:
            logger.info(f'Unable to connect to network through node {host}:{port}. Creating network')
            await self.run()
            return

        self.entry = entry
        logger.info(f'Connected to network through entry node {entry[0]}@{entry[1]}:{entry[2]}')

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
        logger.info(f"Created listener at host 0.0.0.0:{self.listen_port}")

    async def send(self, target: str, name: str, data: dict) -> Connection:
        """
            Sends an event to a specific target
        """
        conn = await self.router.send(target, msgpack.dumps({
            "name":name,
            "data":data
        }))
        return conn
    
    async def emit(self, name: str, data: dict):
        """
            Broadcasts an event to the entire network.
        """

        await self.router.emit(msgpack.dumps({
            "name": name,
            "data": data
        }))

    def on(self, name: str, func: FunctionType):
        """
            Registers callback for event
        """
        if name not in self.callbacks.keys():
            self.callbacks[name] = []
        self.callbacks[name] += [func]

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
                
                if data["type"] in ["node_join","new_node"]:
                    dat = data["data"]
                    logger.info(f'Node {dat[0]}@{dat[2]}:{dat[3]} has joined via node {dat[3]}')
                elif data["type"] == "data":

                    dat = msgpack.loads(data["body"])
                    print(dat)
                    if dat["name"] in self.callbacks.keys():
                        for v in self.callbacks[dat["name"]]:
                            await v(conn,dat["data"])
        except anyio.EndOfStream:
            # Ignore EndOfStream
            logger.debug(f"{conn.host}:{conn.port} disconnected")
        