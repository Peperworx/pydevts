from ..routers import BasicRouter
import anyio
import contextlib
from loguru import logger
import uuid
from .. import error

class P2PConnection:
    """
        Represents a connection to a peer to peer cluster.
    """
    def __init__(self, entry):
        """
            Represents a connection to a peer to peer cluster.
        """
        # Validate entry
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise AttributeError("Entry must be a tuple of (str, int)")
        
        # Check entry[0] is a string
        if not isinstance(entry[0], str):
            raise AttributeError("Entry must be a tuple of (str, int)")
        
        # Check entry[1] is a number / string of number
        if isinstance(entry[1], str):
            if entry[1].isdecimal():
                self.entry = (entry[0], int(entry[1]))
            else:
                raise AttributeError("Entry must be a tuple of (str, int)")
        elif not isinstance(entry[1], int):
            raise AttributeError("Entry must be a tuple of (str, int)")
        else:
            self.entry = entry
        
        self.router = BasicRouter(self)

        # Generate node id
        self.nid = str(uuid.uuid4())

        self.tg = None
    
    async def serve(self, task_status):
        """
            Create anyio TCP listener.
            Use a random open port, and save it to a variable
        """
        # Create async TCP listener (using anyio)
        self.listener = await anyio.create_tcp_listener(local_host="0.0.0.0", local_port=0)
        
        # Get local port from the raw socket of the first listener
        self.port = self.listener.listeners[0]._raw_socket.getsockname()[1]

        # Tell task group we are ready
        task_status.started()

        # Log that we are hosting
        logger.info(f"Serving on port {self.port}")

        # Start server in exit stack
        await self.listener.serve(self.handler)

    @error.catch_all_continue
    async def handler(self, conn):
        """
            Handle a connection
        """
        while True:
            # Pass along to router
            await self.router.receive(conn)

    async def __aenter__(self) -> "P2PConnection":

        # Clear kill flag
        self.kill = False

        # If task group is not None, fail
        if self.tg is not None:
            raise RuntimeError("Connection already in use")

        # Create async exit stack
        self.es = contextlib.AsyncExitStack()


        # Prepare Task Group
        self.tg = await self.es.enter_async_context(anyio.create_task_group())

        

        # Prepare security
        await self.router.prepare_security()

        

        # Connect router to entry node
        self.entry = await self.router.connect_to(self.entry[0], self.entry[1])

        # Call serve function in task group
        await self.tg.start(self.serve)

        # Return self
        return self
    
    async def __aexit__(self, *args) -> "P2PConnection":
        
        # Set kill flag
        self.kill = True

        # Clear exit stack
        await self.es.aclose()

        # Clear task group
        self.tg = None