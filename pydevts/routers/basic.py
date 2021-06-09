"""
    This is a basic implementation of the "Everyone knows Everyone" routing system.
    It does not scale well, but works for testing purposes.
"""

from ._base import RouterBase
from typing import Optional
from pydevts.conn import Connection
import socket
import uuid

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
        
        
        self.peers.append(("entry",host,port))
        
        conn = await self._send("entry", {
            "type":"connect",
            "host": socket.gethostbyname(socket.getfqdn()),
            "port": self.owner.listen_port
        })
        

        data = await conn.recv()
        
        if data["type"] == "ack_connect":
            self.owner.nid = data["uid"]
            self.peers = [(data["my_uid"],host,port)] + data["peers"]
        else:
            raise RuntimeError("Unexpected response")
        
        await self._cleanup()
        print(self.peers)

    
    async def _send(self, target: str, data: dict) -> Connection:
        for p in self.peers:
            if p[0] == target:
                conn = await Connection.connect(p[1],p[2])
                await conn.send(data)
                return conn
    
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
                rmp.append(p)
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
        
        for p in self.peers:
            if p[0] == target:
                conn = await Connection.connect(p[1],p[2])
                await conn.send({"type":"data","body":data})
                return conn

    async def receive(self, conn: Connection) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        
        data = await conn.recv()

        if data["type"] == "connect":
            uid = str(uuid.uuid4())

            await conn.send({
                "type":"ack_connect",
                "uid": uid,
                "my_uid": self.owner.nid,
                "peers":self.peers
            })

            self.peers.append((uid,data["host"],data["port"]))

            await self._cleanup()

            print(self.peers)
        elif data["type"] == "data":
            return data["body"]
            