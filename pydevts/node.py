"""
    This file contains classes for creating nodes on top of P2P connections
"""

from . import p2p
from .conn import Connection


class AsyncCustomInitMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        if "_init" in obj.__dir__():
            obj._init(*args, **kwargs)
        obj.__init__(*args,**kwargs)
        return obj


class Node(metaclass=AsyncCustomInitMeta):
    def __init__(self, *args, **kwargs):
        pass
    
    def _init(self, *args, host: str = "localhost", port: int = "2233", **kwargs):
        """
            Creates a node instance, connection to P2P network {host}:{port}
        """

        self.conn = p2p.P2PNode()
        self.host = host
        self.port = port
        self._info = {}

        self.conn.on("get_data", self.get_data)
        self.conn.on("on_replicate", self.on_replicate)
        self.conn.on("on_fetch", self.on_fetch)
        self.conn.on("on_start", self.on_startup)
    async def run(self):
        await self.conn.join(self.host,self.port)
        
    
    def on(self, name: str):
        """
            Decorator that registers event handler/
        """
        def _deco(func):
            self.conn.on(f"_{name}", func)
            return func
        return _deco
    
    async def emit(self, name: str, data: dict):
        """
            Function that emits an event to all nodes.
        """

        await self.conn.emit(f"_{name}", data)

        
        
    async def send(self, target: str, name: str, data: dict) -> Connection:
        """
            Function that sends evvent to a specific peer, and returns the connection.
        """

        conn = await self.conn.send(target, f"_{name}", data)

        return conn
    
    async def get_data(self, conn: Connection, data: dict):
        """
            Function called when we are asked for data
        """
        await conn.send(self._info)
    
    async def on_startup(self):
        """
            Function called when the node successfully connects to the cluster
        """

        self._info = {
            "id": self.conn.nid,
            "init": False
        }
    

    ##############################
    #      Data Replication
    ##############################


    async def on_replicate(self, conn: Connection, data: dict):
        """
            Function called when data needs to be replicated
        """
        ...
    
    async def on_fetch(self, conn: Connection, data: dict):
        """
            Function called when a node needs to read a value from other nodes.
        """
        ...

class DBNode(Node):
    """
        Basic Node that implements a key/value store
    """
    def __init__(self, *args, **kwargs):
        self.store = {}
    
    def __dict__(self):
        return self.store

    def get(self, k):
        return self.store[k]

    async def set(self, k, v):
        await self.conn.emit("on_replicate",{
            "type":"nodedb",
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

        await self.conn.send(self.conn.entry["nid"], {
            "name": "on_fetch",
            "data": {
                "type": "nodedb",
                "id": self.conn.nid
            }
        })

        
        

    ##############################
    #      Data Replication
    ##############################

    async def on_replicate(self, conn: Connection, data: dict):
        """
            Function called when data needs to be replicated
        """
        
        if data.get("type") != "nodedb":
            return
        self.store[data["key"]] = data["value"]
    


    async def on_fetch(self, conn: Connection, data: dict):
        """
            Function called when a node needs to read a value from other nodes.
        """

        if data.get("type") != "nodedb":
            return
        for k,v in self.store.items():
            await self.conn.send(
                data["id"],
                "on_replicate",
                {
                    "type":"nodedb",
                    "key":k,
                    "value":v
                }
            )