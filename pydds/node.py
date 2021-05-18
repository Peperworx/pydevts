"""
    This file contains classes for creating Nodes on top of P2P Connections
"""

from . import p2p
from .conn import Connection
import trio


class AsyncCustomInitMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        if "_init" in obj.__dir__():
            obj._init(*args, **kwargs)
        obj.__init__(*args, **kwargs)
        return obj

class Node(metaclass=AsyncCustomInitMeta):
    def __init__(self, *args, **kwargs):
        pass
    def _init(self, host, port):
        """
            Creates a node instance.
            Enters P2P network using entry address {host}:{port}
        """

        # Create the connection
        self.conn = p2p.P2PConnection(host, port)

        
        self.events = {}

        # Register the events
        for k,v in self.events.items():
            self.conn.listen(k)(v)
        
        
    async def run(self):
        await self.conn.start()
    
    def on(self, event: str):
        """
            Decorator wrapper that registers events
        """
        def _deco(func):
            self.conn.listen(f"_{event}")(func)
            return func
        return _deco
    
    async def emit(self, event: str, data: dict):
        """
            Wrapper function that emits an event
        """

        # Emit to others
        await self.conn.broadcast(f"_{event}", data)

        # Connect to self and emit
        conn = await trio.open_tcp_stream(
            "localhost",
            self.conn.server.socket.getsockname()[1]
        )

        await self.conn._emit(conn, f"_{event}", data)

    async def send(self, nid: str, event: str, data: dict):
        """
            Allows us to initiate a connection with a peer.
        """
        conn = None

        for peer in self.conn.peers:
            if peer["id"] == nid:
                conn = await Connection.connect(peer["host"],peer["port"])
        
        if nid == self.conn.nid:
            conn = await trio.open_tcp_stream(
                "localhost",
                self.conn.server.socket.getsockname()[1]
            )
        await self.conn._emit(conn, f"_{event}", data)
        return Connection(
            conn
        )
        

    async def on_enter(self):
        """
            Function called when the node successfully connects to the cluster
        """

    ##############################
    #      Data Replication
    ##############################

    async def on_replicate(self, request, data: dict):
        """
            Function called when data needs to be replicated
        """
        ...
    


    async def on_fetch(self, request, data: dict):
        """
            Function called when a node needs to read a value from other nodes.
        """
        ...
    
    
    

class DBNode(Node):
    """
        Basic Node that implements a key/value store
    """

    
    

        
