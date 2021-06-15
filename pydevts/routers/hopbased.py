"""
    Hop based everyone knows everyone system.
    This is really scalable, and works best with chains of nodes.

    We will be using a lot of concepts from basic EKERouter

    This system is in no way foolproof as it a connection is dropped or a node goes offline, connected nodes
    may be dropped from the network. This is only a proof of concept, and future systems will be
    implemented that are much more robust.
"""

from typing import Optional
from pydevts.routers._base import RouterBase
from pydevts import Connection
import struct
import msgpack
import uuid
import networkx as nx

class HopBasedRouter(RouterBase):

    # Types of requests
    

    def __init__(self, owner, **router_config):
        self.owner = owner
        self.config = router_config

        # These are different.
        self.peers = [] # Peers are immediate neighbors
        self.nodes = {} # Nodes are everyone on the network
        self.entry = None # The entry node
    
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
            conn = await Connection.connect(host, port)
        except OSError:
            return None

        # Generate and send request
        await conn.send(
            struct.pack("!B",1) # 1 is info request
        )

        # Receive response
        data = await conn.recv()

        # Unpack the message type
        msg_type = struct.unpack("!B",data[:struct.calcsize("!B")])[0]
        data = data[struct.calcsize("!B"):]

        # If not a response, return none
        if msg_type != 2:
            return None
        
        # Load Message size
        msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
        data = data[struct.calcsize("!L"):]

        # Load entry node data
        entry = msgpack.loads(data[:msg_size])


        # Set entry node info
        entry = (
            entry[0],   # Entry nid
            conn.host,  # Entry host
            entry[1],   # Entry port
            entry[2],   # Entry entry
            entry[3],   # Entry peers
        )

        # Add entry to list of peers
        self.peers += [entry]

        # Request entry notify
        # TODO: Auth here

        dat = msgpack.dumps((
            self.owner.listen_port,
            [p[0] for p in self.peers]
        ))
        await conn.send(
            struct.pack("!B",3)+
            struct.pack("!L",len(dat))+
            dat)

        # Receive response
        data = await conn.recv()

        # Unpack the message type
        msg_type = struct.unpack("!B",data[:struct.calcsize("!B")])[0]
        data = data[struct.calcsize("!B"):]

        # If not a response, return none
        if msg_type != 4:
            return None
        
        # Load Message size
        msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
        data = data[struct.calcsize("!L"):]

        # Load message
        info = msgpack.loads(data[:msg_size])

        # Update our info
        self.owner.nid = info[0]

        # Set our entry node
        self.entry = info[3]
        
        # Set our node dict
        self.nodes ={k:set(v) for k,v in info[5].items()}

        # Set the peers of our entry node
        self.nodes[entry[0]] = set([e[0] for e in entry[4]])
        print(f"My ID: {self.owner.nid}")

        # Return entry info
        return entry



    
    async def emit(self, data: bytes):
        """
            Executed when a node wants to broadcast raw data
            Arguments
            - {data}
                The raw data in bytes
        """
        
        # This is simple. Just iterate over each node and send
        for n in self.nodes.keys():
            await self.send(n,data)

    async def send(self, target: str, data: bytes):
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """
        
        # Generate graph from node list
        g = nx.from_dict_of_lists(self.nodes | {self.owner.nid: set([p[0] for p in self.peers])})

        # Get shortest path
        sp = nx.shortest_path(g,self.owner.nid,target)

        # Get the first one
        spf = sp[0]

        if spf == self.owner.nid and len(sp) > 1:
            spf = sp[1]
        
        # Find it and send
        for p in self.peers.copy():
            try:
                if p[0] == spf:
                    dat = msgpack.dumps({
                        "target":target,
                        "data":data
                    })
                    conn = await Connection.connect(
                        p[1],
                        p[2]
                    )
                    await conn.send(
                        struct.pack("!B",6)+        # Number 6 is relay
                        struct.pack("!L", len(dat))+# Length of data
                        dat                         # The data
                    )
                    return conn
            except OSError:
                self.peers.remove(p)
        
        if target == self.owner.nid:
            dat = msgpack.dumps({
                "target":target,
                "data":data
            })
            conn = await Connection.connect(
                "localhost",
                self.owner.listen_port
            )
            await conn.send(
                struct.pack("!B",6)+        # Number 6 is relay
                struct.pack("!L", len(dat))+# Length of data
                dat                         # The data
            )
            return conn
        
        raise RuntimeError(f"Unable to connect to peer {target}")

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

        
        # If it is ping, respond with ping
        if msg_type == 0:
            await conn.send(struct.pack("!B",0))
        elif msg_type == 1: # If it is a info request, respond with info
            dat = msgpack.dumps((
                self.owner.nid, # Node ID
                self.owner.listen_port, # Listen Port
                self.entry if self.entry else self.owner.nid, # Our entry node
                self.peers, # Peers
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

            ng = {k:list(v) for k,v in self.nodes.items()}

            # Generate info
            newinfo = (
                str(uuid.uuid4()),   # Generate new nid
                conn.host,      # The node host
                data[0],        # The node Port
                self.owner.nid, # The entry node
                data[1],        # The peers of the new node
                ng              # The network graph
            )

            dat = msgpack.dumps(newinfo)
            dat2 = msgpack.dumps(newinfo[:5])
            
            # Send info
            await conn.send(
                struct.pack("!B", 4)+
                struct.pack("!L",len(dat))+
                dat
            )

            # Copy peer list
            pc = self.peers.copy()

            # Add to peers
            self.peers += [newinfo]

            # Add to nodes
            self.nodes[newinfo[0]] = set(newinfo[4])

            # Iterate over peers, sending to each
            for p in pc:
                try:
                    c = await Connection.connect(p[1],p[2])
                    await c.send(
                        struct.pack("!B",5)+
                        struct.pack("!L",len(dat2))+
                        dat2
                    )
                except OSError:
                    self.peers.remove(p)
            
            return {
                "type":"node_join",
                "data":newinfo[:5]
            }
        elif msg_type == 5:
            msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
            data = data[struct.calcsize("!L"):]

            data = msgpack.loads(data[:msg_size])
            
            if data[0] not in self.nodes.keys():
                # Add the node to the entry node
                self.nodes[data[3]] |= {data[0],}

                # Add the node to nodes
                self.nodes[data[0]] = set(data[4])
                dat = msgpack.dumps(data)
                # Pass along
                for p in self.peers.copy():
                    try:
                        c = await Connection.connect(p[1],p[2])
                        await c.send(
                            struct.pack("!B",5)+
                            struct.pack("!L",len(dat))+
                            dat
                        )
                    except OSError:
                        self.peers.remove(p)
                return {
                    "type":"node_join",
                    "data":data
                }
            # Done!
        elif msg_type == 6:
            msg_size = struct.unpack("!L",data[:struct.calcsize("!L")])[0]
            data = data[struct.calcsize("!L"):]

            data = msgpack.loads(data[:msg_size])
            
            if data["target"] == self.owner.nid:
                return {
                    "type":"data",
                    "body":data["data"]
                }
            
            # If it is not us, forward
            await self.send(data["target"],data["data"])
        
        return {"type":"no_info"}
    

