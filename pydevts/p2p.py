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

    known_nodes: list[str] # A List of the NIDs of all known nodes.
    nid: str # The node ID of this node
    server: MultiListener # The anyio server listener
    listen_port: int # The port to listen on


    def __init__(self):
        """
            A basic multi peer peer to peer node.
        """
        self.known_nodes = []
        self.nid = uuid.uuid4()
    
    async def join(self,host,port):
        """
            Join a cluster.
        """
        
        # Initialize local server
        await self._initialize()


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

        # Loop until we fail
        while True:
            raise Exception("yeehaw")