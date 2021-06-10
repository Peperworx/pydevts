"""
    This is a basic implementation of the "Everyone knows Everyone" routing system.
    It does not scale well, but works for testing purposes.
"""

from ._base import RouterBase
from typing import Optional
from pydevts.conn import Connection
import socket
import uuid
import anyio

class EKERouter(RouterBase):
    """
        Basic implementation of "Everyone knows Everyone" routing system as described in pydevts/routers/README.md
    """

    def __init__(self, owner, **router_config):
        self.owner = owner
        self.config = router_config
        self.peers = []
    
    
    async def connect_to(self, host: str, port: int):
        """
            Executed when node is attempting to connect to cluster
            Arguments
            - {host}
                Host of the entry node
            - {port}
                Port of the entry node
        """
        
        try:
            conn = await Connection.connect(host,port)
        except OSError:
            
            return None
        await conn.send({
            "type":"peer_connect",
            "port": self.owner.listen_port,

        })
        
        
        
        data = await conn.recv()
        
        
        if data["type"] == "ack_connect":
            self.owner.nid = data["nid"]
            self.peers = [(data["entry_nid"],host,port,conn.port)] + data["peers"]
        else:
            raise RuntimeError("Unexpected response")
        
        await self._cleanup()
        

        return {
            "entry":{
                "nid": data["entry_nid"],
                "host": conn.host,
                "port": port,
                "cliport": conn.port,
            }
        }
    
    async def emit(self, data: bytes):
        """
            Executed when a noad wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """
        rmp = []
        for p in self.peers:
            try:
                conn = await Connection.connect(p[1],p[2])
                await conn.send({"type":"data","bcast":True,"body":data})
                await conn.aclose()
            except OSError:
                rmp += [p]
        [self.peers.remove(p) for p in rmp]

        


    
    async def _send(self, target: str, data: dict) -> Connection:
        rmp = []
        for p in self.peers:
            try:
                if p[0] == target:
                    conn = await Connection.connect(p[1],p[2])
                    await conn.send(data)
                    return conn
            except OSError:
                rmp += [p]
        [self.peers.remove(p) for p in rmp]
    
    async def _cleanup(self):
        """
            Iterates over each peer, cleaning up those that are no longer online
        """
        rmp = []
        for p in self.peers:
            try:
                conn = await Connection.connect(p[1],p[2])

                await conn.send({"type":"ping"})

                await conn.aclose()
            except OSError:
                rmp += [p]
        [self.peers.remove(p) for p in rmp]
        
    async def send(self, target: str, data: bytes) -> Connection:
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """

        if target == self.owner.nid:
            conn = await Connection.connect("localhost", self.owner.listen_port)
            await conn.send({"type":"data","bcast":False,"body":data})
            return conn
        rmp = []
        for p in self.peers:
            try:
                if p[0] == target:
                    conn = await Connection.connect(p[1],p[2])
                    await conn.send({"type":"data","bcast":False,"body":data})
                    return conn
            except OSError:
                rmp += [p]
        [self.peers.remove(p) for p in rmp]

        
    
    async def receive(self, conn: Connection) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        
        data = await conn.recv()

        if data["type"] == "peer_connect":
            nid = str(uuid.uuid4())

            await conn.send({
                "type":"ack_connect",
                "nid": nid,
                "entry_nid": self.owner.nid,
                "peers":self.peers
            })
            rmp = []
            for peer in self.peers:
                try:
                    conn = await Connection.connect(peer[1],peer[2])
                    await conn.send({
                        "type": "peer_join",
                        "nid": nid,
                        "host": conn.host,
                        "port": data["port"],
                        "entry": self.owner.nid,
                        "cliport": conn.port,
                    })
                    await conn.aclose()
                except OSError:
                    rmp += [peer]
            [self.peers.remove(i) for i in rmp]

            self.peers.append((nid,conn.host,data["port"],conn.port))

            await self._cleanup()

            
            data["nid"] = nid
            data["host"] = conn.host
            data["cliport"] = conn.port
            return data
        elif data["type"] == "peer_join":
            self.peers.append((
                data["nid"],
                conn.host,
                data["port"],
                data["cliport"]
            ))

            await self._cleanup()
            
            
            return data
        return data
            