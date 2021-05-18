"""
    This file contains classes for creating Nodes on top of P2P Connections
"""

from . import p2p

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

        
        self.events = {
            "on_startup":self.on_startup,
            "get_keys": self.get_keys,
            "keys_fetched": self.keys_fetched,
            "on_fetch": self.on_fetch,
            "on_replicate": self.on_replicate
        }

        # Register the events
        for k,v in self.events.items():
            self.conn.listen(k)(v)
        
        
    async def run(self):
        await self.conn.start()
    
    async def on_startup(self):
        """
            Startup function
        """

        pass
    
    async def on_replicate(self, data: dict):
        """
            When data is replicated, this function is called
        """

        pass
    
    async def on_fetch(self, data: dict):
        """
            When someone needs to fetch data, this function is called
        """

        pass
    
    async def get_keys(self, data: dict):
        """
            Called when we need to send a client what keys we have
        """

        pass

    async def keys_fetched(self, data: dict):
        """
            Called when we recieve the keys
        """
        pass

class DBNode(Node):
    """
        Basic Node that implements a key/value store
    """

    def __init__(self, *args, **kwargs):
        self.store = {}
        

    async def on_startup(self):
        print(self.conn.nid)
        # Request list of keys
        await self.conn.broadcast("get_keys",{
            "id":self.conn.nid
        })
    
    async def get_keys(self, data: dict):
        
        if len(self.store.keys()) > 0:
            # Send the keys
            await self.conn.sendto(
                data["id"],
                "keys_fetched",
                {
                    "keys":list(self.store.keys())
                }
            )
    
    async def keys_fetched(self, data: dict):
        keys = set(self.store.keys())
        keys.update(data["keys"])
        for k in keys:
            if k not in self.store.keys():
                self.store[k] = None
    
    async def on_fetch(self, data: dict):
        if self.store[data["key"]]:
            await self.conn.sendto(data["id"],"on_replicate",{
                "key":data["key"],
                "value":self.store[data["key"]]
            })
    
    async def on_replicate(self, data: dict):
        self.store[data["key"]] = data["value"]

    async def __getitem__(self,key):
        if key not in self.store.keys():
            return None
        
        if self.store[key] == None:
            await self.conn.broadcast(
                "on_fetch",
                {
                    "id":self.conn.nid,
                    "key":key
                }
            )
        return self.store[key]
    async def __setitem__(self, key, value):
        self.store[key] = value
        await self.conn.broadcast(
            "on_replicate",
            {"key":key,"value":value}
        )
    

        
