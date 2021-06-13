"""
    Hop based everyone knows everyone system.
    This is really scalable, and works best with chains of nodes.

    We will be using alot of concepts from basic EKERouter
"""

from typing import Optional
from pydevts.routers._base import RouterBase
from pydevts import Connection

class HopBasedRouter(RouterBase):

    # Types of requests
    

    def __init__(self, owner, **router_config):
        self.owner = owner
        self.config = router_config

        # These are different.
        self.peers = [] # Peers are immediate neighbors
        self.nodes = {} # Nodes are everyone on the network
    
    
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
            # Connect to entry node
            conn = Connection.connect(host, port)
        except OSError:
            return None

        # Generate and send request
        await conn.send(
            struct.pack("!B",1) # 1 is info request
        )

        # Receive response
        data = await conn.recv()

        print(data)
    
    async def emit(self, data: bytes):
        """
            Executed when a noad wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """
        pass

    async def send(self, target: str, data: bytes):
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """
        pass

    async def receive(self, data: bytes) -> Optional[bytes]:
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

        # If it is ping, respond with ping
        if msg_type == 0:
            await conn.send(struct.pack("!B",0))
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
                conn.host,      # The node host
                data[0],        # The node Port
                self.owner.nid, # The entry node
            )

            dat = msgpack.dumps(newinfo)

            # Send info
            await conn.send(
                struct.pack("!B", 4)+
                struct.pack("!L",len(dat))+
                dat
            )

            # Iterate over peers, sending to each
            for p in self.peers:
                c = await Connection.connect(p[2],p[3])
                await c.send(
                    struct.pack("!B",4)
                )
    

