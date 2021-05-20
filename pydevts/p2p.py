"""
    Contains classes that represent multi-node peer to peer connections with message routing.
"""

import uuid
import socket
import os

import anyio
from loguru import logger

from .connection import *
from . import errors

# We need some secret stuff :)
from anyio.streams.stapled import MultiListener
from anyio.abc._sockets import SocketStream


class P2PNode:
    """
        A basic peer to peer node.
    """

    known_nodes: dict[str,dict] # A List of the NIDs of all known nodes.
    nid: str # The node ID of this node
    server: MultiListener # The anyio server listener
    listen_port: int # The port to listen on


    def __init__(self):
        """
            A basic multi peer peer to peer node.
        """
        self.known_nodes = {}
        self.nid = str(uuid.uuid4())
    
    async def join(self,host: str,port: int):
        """
            Join a cluster.
        """
        
        # Initialize local server
        await self._initialize()


        # Initiate a connection with the server
        try:
            conn = Connection(await anyio.connect_tcp(
                remote_host = host,
                remote_port = port
            ))
        except:
            logger.warning(f"Unable to connect to {host}:{port}. Continuing")
            return
        
        # Prepare test payload
        test_payload = {"type":"status","random":os.urandom(32).hex()}

        # Send payload
        await conn.send(test_payload)

        # Receive test.
        returned_test = await conn.recv()

        # If they are not the same, just exit and be ready to start.
        if test_payload != returned_test:
            logger.warning(f"Unable to connect to {host}:{port}. Continuing")
            return
        
        # Request to join.
        # TODO: Credentials here
        await conn.send({
            "type":"register",
            "port":self.listen_port
        })

        # Receive details
        details = await conn.recv()
        if details["type"] == "prepare_accept":
            logger.debug("This node has been accepted to the cluster.")
            self.nid = details["nid"]
            self.known_nodes = details["known_nodes"]
        
        # Request the graph
        await conn.send({
            "type":"graph",
            "redirect_port":self.listen_port,
            "graph":{}
        })

        await self.run()


    async def start(self):
        """
            Start a cluster
        """

        # Initialize local server
        await self._initialize()

        # That is all we need to do to start an empty cluster! Cool!
        
    
    async def _initialize(self):
        """
            Internal function to initialize peer to peer functionalities.
            Sets up a local server.
        """

        # Create listeners
        self.server = await anyio.create_tcp_listener(
            local_host="0.0.0.0", # All Ips
            local_port=0 # Choose a port
        )

        # Our listen port
        self.listen_port = self.server.listeners[0]._raw_socket.getsockname()[1]


        # Log
        logger.debug(f"Created listener at host 0.0.0.0:{self.listen_port}")



    async def run(self):
        """
            Begin executing server.
        """
        
        # Start serving
        await self.server.serve(self._serve)
    
    @errors.catch_all_continue
    async def _serve(self, ss: SocketStream):
        """
            Handler called on each request
        """
        
        # Wrap the connection
        conn = Connection(ss)

        # Grab the host and port
        host = ss._raw_socket.getpeername()[0]
        port = ss._raw_socket.getpeername()[1]

        logger.debug(f"Connection from {host}:{port}")

        try:
            # Loop until we fail
            async for data in conn:

                if data["type"] == "status":
                    await conn.send(data)
                elif data["type"] == "register":
                    logger.debug(f"{host}:{port} wants to join the cluster")
                    await self._node_registers(conn, data, host, port)
                elif data["type"] == "graph":
                    await self._request_graph(conn, data, host, port)
                
        except anyio.EndOfStream:
            # Ignore EndOfStream
            logger.debug(f"{host}:{port} disconnected")
    
    async def _node_registers(self, conn, data, host, port):
        """
            This function is called when a node attempts to connect to the cluster.
        """
        # TODO: Authentication here

        # Issue a node id
        nid = str(uuid.uuid4())

        

        # Tell the client they have been accepted
        # Include the nodes that we know, including ourselves.
        await conn.send({
            "type":"prepare_accept",
            "from":self.nid,
            "nid":nid,
            "known_nodes":self.known_nodes | {
                self.nid:{
                    "host": socket.gethostbyname(socket.gethostname()),
                    "port": self.listen_port,
                }
            }
        })


        # Add to nodes
        self.known_nodes[nid] = {
            "host":host,
            "port":data["port"]
        }
        

        logger.info(f"Peer {nid} has joined the cluster.")

    async def recursive_request_graph(self, graph):
        pass

    async def _request_graph(self, conn, data, host, port):
        """
            Returns the graph of the cluster
        """
        graph = data["graph"] | {
            self.nid:list(self.known_nodes.keys())
        }
        print(graph)
        # Now for each of the keys we know, request the graph
        for k,peer in self.known_nodes.items():
            if k not in graph.keys():
                conn = Connection(await anyio.connect_tcp(
                    remote_host = peer["host"],
                    remote_port = peer["port"]
                ))
                print(k)
                await conn.send({"type":"graph","graph":graph})
                g = await conn.recv()
                graph[k] = g[k]
        
        print("graph")

        await conn.send(graph)