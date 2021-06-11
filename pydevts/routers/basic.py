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

        # Initialize list of our peers
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
        
        # Attempt to connect to the entry node
        try:
            conn = await Connection.connect(host,port)
        except OSError:
            return None
        
        # Tell the entry node that we are connecting.
        await conn.send({
            "type":"peer_connect",
            "port": self.owner.listen_port,
        })
        
    
    async def emit(self, data: bytes):
        """
            Executed when a noad wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """

        pass

        


    
    async def _send(self, target: str, data: dict) -> Connection:
        pass
    
    
        
    async def send(self, target: str, data: bytes) -> Connection:
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """

        pass

        
    
    async def receive(self, conn: Connection) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        
        pass
            