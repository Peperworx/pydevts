"""
    This file contains classes for creating nodes on top of P2P connections
"""

from . import p2p



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

        