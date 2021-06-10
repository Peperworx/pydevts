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
        
        
        # Receive data
        data = await conn.recv()
        
        # If it was an acknowledgment 
        if data["type"] == "ack_connect":

            # Set our new nid (We recieve it from the entry node
            # to hinder spoofing)
            self.owner.nid = data["nid"]

            # Set our list of peers the same as the entry node + the entry node
            self.peers = [(data["entry_nid"],host,port,conn.port)] + data["peers"]
        else:
            # If not, somemthing went wrong
            raise RuntimeError("Unexpected response")
        
        # Clean up out list of peers.
        await self._cleanup()
        
        # Return entry node details, including the client port.
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

        # Create list of peers to remove
        rmp = []

        # Iterate over peers
        for p in self.peers:
            try:
                # Connect and send the message
                conn = await Connection.connect(p[1],p[2])
                await conn.send({"type":"data","bcast":True,"body":data})
                await conn.aclose()
            except OSError:
                # If we fail to connect, add the peer
                # to the list of peers to remove
                rmp += [p]
        
        # Remove all peers in rmp
        [self.peers.remove(p) for p in rmp]

        


    
    async def _send(self, target: str, data: dict) -> Connection:

        # Create list of peers to remove
        rmp = []

        # Iterate over peers
        for p in self.peers:
            try:
                # If it is out target connect and send
                if p[0] == target:
                    conn = await Connection.connect(p[1],p[2])
                    await conn.send(data)
                    return conn
            except OSError:
                # If we fail to connect, add peer to list of peers to remove
                rmp += [p]
        
        # Remove all peers in rmp
        [self.peers.remove(p) for p in rmp]
    
    async def _cleanup(self):
        """
            Iterates over each peer, cleaning up those that are no longer online
        """

        # Create list of peers to remove
        rmp = []

        # Iterate over peers
        for p in self.peers:
            try:
                # If it is out target connect and send
                conn = await Connection.connect(p[1],p[2])

                await conn.send({"type":"ping"})

                await conn.aclose()
            except OSError:
                # If we fail to connect, add peer to list of peers to remove
                rmp += [p]
        
        # Remove all peers in rmp
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

        # If the target is us
        if target == self.owner.nid:
            # Connect to ourselves and send
            conn = await Connection.connect("localhost", self.owner.listen_port)
            await conn.send({"type":"data","bcast":False,"body":data})
            return conn # Return the connection
        
        # Create a list of peers to remove
        rmp = []

        # Iterate over peers
        for p in self.peers:
            try:
                # If it is our target, send and return the connection.
                if p[0] == target:
                    conn = await Connection.connect(p[1],p[2])
                    await conn.send({"type":"data","bcast":False,"body":data})
                    return conn
            except OSError:
                # If the connection fails, add to list of peers to remove
                rmp += [p]
        
        # Remove all peers in rmp
        [self.peers.remove(p) for p in rmp]

        
    
    async def receive(self, conn: Connection) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        
        # Receive the daya
        data = await conn.recv()

        # If it is a peer connecting
        if data["type"] == "peer_connect":
            # Generate an nid
            nid = str(uuid.uuid4())

            # Send the required info
            await conn.send({
                "type":"ack_connect",
                "nid": nid,
                "entry_nid": self.owner.nid,
                "peers":self.peers
            })

            # Iterate over peers and send info about new peer,
            # similar to in the self.send function
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

            # Add the peer to out list
            self.peers.append((nid,conn.host,data["port"],conn.port))

            # Cleanup peers
            await self._cleanup()

            # Add required info to data
            data["nid"] = nid
            data["host"] = conn.host
            data["cliport"] = conn.port

            # Return data
            return data
        
        # If it is a peer notifying us of another peer joining
        elif data["type"] == "peer_join":
            # Add the peer to our list
            self.peers.append((
                data["nid"],
                conn.host,
                data["port"],
                data["cliport"]
            ))

            # Cleanup list of peers
            await self._cleanup()
            
            # Return data
            return data

        # If none match, return data
        return data
            