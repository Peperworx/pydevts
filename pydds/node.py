"""
    This file contains classes for creating Nodes on top of P2P Connections
"""

from . import p2p

import trio


class AsyncCustomInitMeta(type):
    async def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        if "_init" in obj.__dir__():
            await obj._init(*args, **kwargs)
        obj.__init__(*args, **kwargs)
        return obj

class Node(metaclass=AsyncCustomInitMeta):
    def __init__(self, *args, **kwargs):
        pass
    async def _init(self, host, port):
        """
            Creates a node instance.
            Enters P2P network using entry address {host}:{port}
        """

        # Create the connection
        self.conn = p2p.P2PConnection(host, port)

        self.events = {
            "on_startup":self.on_startup
        }

        # Register the events
        for k,v in self.events.items():
            self.conn.listen(k)(v)
        
        
        
    async def run(self):
        await self.conn.start()
    
    async def on_startup(self):
        """
            Internal startup function
        """

        # Request keys from cluster
        self.conn.send(0,"request_keys")
        