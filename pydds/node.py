"""
    This file contains classes for creating Nodes on top of P2P Connections
"""

from . import p2p
from .conn import Connection
import trio


class AsyncCustomInitMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj.host = kwargs["host"] if "host" in kwargs.keys() else "localhost"
        obj.port = int(kwargs["port"]) if "port" in kwargs.keys() else 2233
        if "_init" in obj.__dir__():
            obj._init()
        del kwargs["port"]
        del kwargs["host"]
        obj.__init__(*args, **kwargs)
        return obj

class Node(metaclass=AsyncCustomInitMeta):
    def __init__(self, *args, **kwargs):
        pass
    def _init(self):
        """
            Creates a node instance.
            Enters P2P network using entry address {host}:{port}
        """

        # Create the connection
        self.conn = p2p.P2PConnection(self.host, self.port)

        
        self.events = {
            "on_startup": self.on_startup,
            "on_replicate": self.on_replicate,
            "on_fetch": self.on_fetch,
            "get_data": self.get_data,
        }

        # Register the events
        for k,v in self.events.items():
            self.conn.listen(k)(v)
        
        self._info = {
        }
        
        
        
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
                conn = await trio.open_tcp_stream(peer["host"],peer["port"])
        
        if nid == self.conn.nid:
            conn = await trio.open_tcp_stream(
                "localhost",
                self.conn.server.socket.getsockname()[1]
            )
        await self.conn._emit(conn, f"_{event}", data)
        return Connection(
            conn
        )
    
    async def find_node(self, func):
        """
            Iterates over peers, retrieving the internal data stores.
            Takes a function, func that returns whether or not to choose the passed peer.
            Returns the first peer for which the function returns true
        """
        for peer in self.conn.peers:
            conn = await trio.open_tcp_stream(peer["host"],peer["port"])
            await self.conn._emit(conn, f"get_data", "")
            data = await self.conn._recv(conn)
            if func(data):
                return peer
        
        return None
    
    async def get_data(self, request, data):
        """
            Function that is called when we are asked for data
        """
        await request.send(self._info)

    async def on_startup(self):
        """
            Function called when the node successfully connects to the cluster
        """
        
        self._info = {
            "id":self.conn.nid,
            "init":False
        }
    
    

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
    def __init__(self):
        self.store = {}
    
    def __dict__(self):
        return self.store

    def get(self, k):
        return self.store[k]

    async def set(self, k, v):
        await self.conn.broadcast("on_replicate",{
            "key":k,
            "value":v
        })

        self.store[k] = v

    async def on_startup(self):
        """
            Function called when the node successfully connects to the cluster
        """

        self._info = {
            "id":self.conn.nid,
            "keys_known":[],
            "init":False
        }
        
        
        if len(self.conn.peers) == 0:
            self._info["init"] = True
            return

        n = await self.find_node(lambda a: a["init"]==True)
        
        if not n: # If we can find no other initialized nodes, just continue
            self._info["init"] = True
            return

        # Create connection to this peer
        cn: Connection = await Connection.connect(n["host"],n["port"])

        # Send a message
        await cn.send({
            "type":"message",
            "from":self.conn.nid,
            "port":self.conn.server.socket.getsockname()[1],
            "name":"on_fetch",
            "data":{
                "type":"nodedb",
                "id":self.conn.nid
            }
        })
        

    ##############################
    #      Data Replication
    ##############################

    async def on_replicate(self, request, data: dict):
        """
            Function called when data needs to be replicated
        """
        if data.get("type") != "nodedb":
            return
        self.store[data["key"]] = data["value"]
    


    async def on_fetch(self, request, data: dict):
        """
            Function called when a node needs to read a value from other nodes.
        """

        if data.get("type") != "nodedb":
            return
        for k,v in self.store.items():
            await self.conn.sendto(
                data["id"],
                "on_replicate",
                {
                    "type":"nodedb",
                    "key":k,
                    "value":v
                }
            )

    
    
    

        
