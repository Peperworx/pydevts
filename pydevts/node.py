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

        self.conn.on("_get_data", self.get_data)
        self.conn.on("_on_replicate", self.on_replicate)
        self.conn.on("_on_fetch")
    
    async def run(self):
        await self.conn.join(self.host,self.port)
        await self.conn.run()
    
    def on(self, name: str):
        """
            Decorator that registers event handler/
        """
        def _deco(func):
            self.conn.on(name, func)
            return func
        return _deco
    
    async def emit(self, name: str, data: dict):
        """
            Function that emits an event to all nodes.
        """

        await self.conn.emit(name, data)

        if name in self.conn.callbacks.keys():
            for v in self.conn.callbacks[name]:
                await v(data)
        
    async def send(self, target: str, name: str, data: dict) -> Connection:
        """
            Function that sends evvent to a specific peer, and returns the connection.
        """

        conn = await self.conn.send(target, name, data)

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
    