"""
    This is a basic implementation of the "Everyone knows Everyone" routing system.
    It does not scale well, but works for testing purposes.
"""

from ._base import RouterBase
from typing import Optional
from pydevts.conn import Connection
import socket
import struct
import uuid
import anyio
import msgpack

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
        
        # Connect to the host
        conn = await Connection.connect(host, port)

        # Generate and send request
        await conn.send(
            struct.pack("B",1) # 1 is info request
        )

        # Receive response
        data = await conn.recv()
        
        # Unpack type
        msg_type = struct.unpack("!B",data[:struct.calcsize("!B")])[0]
        data = data[struct.calcsize("!B"):]
        print(msg_type)
        if msg_type != 2:
            # If it is not a response, then return None
            return None
        msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
        data = data[struct.calcsize("!L"):]
        entry = msgpack.loads(data[:msg_size])
        
        print(entry)
        # If it is, request to join
        dat = msgpack.dumps((
            self.owner.listen_port,
        ))
        await conn.send(
            struct.pack("!B",3)+
            struct.pack("!L",len(dat))+
            dat)
        
        # Await info
        data = await conn.recv()
        msg_type = struct.unpack("!B",data[:struct.calcsize("!B")])[0]
        data = data[struct.calcsize("!B"):]
        if msg_type != 4:
            # If it is not a response, then return None
            return None
        msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
        data = data[struct.calcsize("!L"):]


        cluster_info = msgpack.loads(data)

        print(cluster_info)
    
    async def emit(self, data: bytes):
        """
            Executed when a noad wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """

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
            - {conn}
                The connection object
        """
        
        # Receive data
        data = await conn.recv()

        # Unpack type
        msg_type = struct.unpack("!B",data[:struct.calcsize("!B")])[0]
        data = data[struct.calcsize("!B"):]

        # If it is a ping, respond with ping
        if msg_type == 0:
            await conn.send(struct.pack("B",0))
        elif msg_type == 1: # If it is a info request, respond with info
            
            dat = msgpack.dumps((
                self.owner.nid, # Node ID
                self.owner.listen_port, # Listen Port
            ))
            resp = struct.pack("!B",2)
            resp += struct.pack("!L",len(dat))
            resp += dat
            await conn.send(resp)
        elif msg_type == 3: # If it is a request to join, accept
            # TODO: Auth here
            msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
            data = data[struct.calcsize("!L"):]

            data = msgpack.loads(data[:msg_size])
            
            # Generate info
            newinfo = (
                str(uuid.uuid4()),   # Generate new nid
                self.peers,     # Our peers
                conn.host,      # The node host
                data[0],
                self.owner.nid, # The entry node
            )
            dat = msgpack.dumps(newinfo)

            # Send info
            await conn.send(
                struct.pack("!B",4)+
                struct.pack("!L",len(dat))+
                dat
            )

            # Iterate over peers, sending to each
            for p in self.peers:
                c = await Connection.connect(p[2],p[3])
                # Tell peer that we have a new node
                await c.send(
                    struct.pack("!B",4)+
                    struct.pack("!L",len(dat))+
                    dat
                )
                await c.aclose()
            
            # Add to peers
            self.peers.append(newinfo)

            return {
                "type":"node_join",
                "data":newinfo
            }
        elif msg_type == 4: # If it is a new node, add
            msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
            data = data[struct.calcsize("!L"):]

            data = msgpack.loads(data[:msg_size])
            self.peers.append(data)
            return {
                "type":"new_node",
                "data":data
            }
        return {
            "type":"no-info"
        }

            