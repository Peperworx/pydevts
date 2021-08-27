"""
    Basic peer-based routing system
"""

# Logging
import msgpack
from ..logger import logger

# Unique IDs
import uuid

# Router parent
from ._base import _Router

# Type Hints
from ..connwrapper import _WrappedConnection
from typing import Callable
import ssl

# Node hosts and connections
from ..host import NodeHost
from ..conn import NodeConnection

class PeerRouter(_Router):
    """Peer-based routing system
    """

    ssl_context: ssl.SSLContext
    host: str
    port: int
    host_addr: tuple[str, int]
    tls: bool
    verify_key: str
    connection: NodeConnection
    entry: str
    node_id: str
    peers: dict[str, tuple[str, int]]

    def __init__(self, ssl_context: ssl.SSLContext = None):
        """Initialize the router

        Args:
            ssl_context (tuple[str, str], optional): The public-private ssl_context to use for encryption. Defaults to None.
        """

        self.ssl_context = ssl_context

        self.peers = dict()
    
    async def enter(self, host: str, port: int, host_addr: tuple[str, int], tls: bool = False, verify_key: str = None):
        """Enters a cluster

        Args:
            host (str): The entry host of the cluster
            port (int): The entry port of the cluster
            host_addr (tuple[str, int]): The address that we are hosting on
            tls (bool, optional): Whether to use TLS. Defaults to False.
            verify_key (str, optional): The verify key to use for TLS. Defaults to None.
        """

        # Save values passed
        self.host = host
        self.port = port
        self.tls = tls
        self.verify_key = verify_key
        self.host_addr = host_addr

        # Create the connection
        self.connection = NodeConnection(self.verify_key)

        # Wrap with try, except so that we can detect if the connection fails
        try:
            # Connect to the entry node
            self.entry = await self.connection.connect(host, port, tls)

            # Tell entry that we have joined
            await self.connection.send(self.entry, b'JOIN', (host_addr,))

            # Await our connection info
            conn_info = await self.connection.recv(self.entry)

            print(conn_info)
        except OSError:
            logger.warning(f"Unable to connect to cluster at {host}:{port}. Starting new cluster")
            self.node_id = str(uuid.uuid4())
        
    
    async def sendto(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        # Open connection
        connection = await self.connection.connect(self.peers[node_id][0], self.peers[node_id][1], self.tls)

        # Send data
        await self.connection.send(connection, data)

        # Close connection
        await connection.close()
    
    async def emit(self, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            data (bytes): The data to emit
        """

        raise NotImplementedError()

    
    async def _emit(self, name: str, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            name (str): The name of the event
            data (bytes): The data to emit
        """

        # Send to all peers
        for peer in self.peers.keys():
            handle = await self.connection.connect(self.peers[peer][0], self.peers[peer][1], self.tls)
            await self.connection.send(handle, name, data)
            await self.connection.disconnect(handle)
        
        # Send to self
        print(self.host_addr)
        handle = await self.connection.connect(*self.host_addr, self.tls)
        await self.connection.send(handle, name, data)
        await self.connection.disconnect(handle)
    
    async def register_handler(self, datahandler: Callable[[bytes],None]):
        """Registers the data handler
        
        Args:
            datahandler (Callable[[bytes],None]): The data handler
        """

        raise NotImplementedError()

    async def on_connection(self, connection: _WrappedConnection):
        """Handles a new connection
        
        Args:
            connection (connwrapper._WrappedConnection): The connection to handle
        """

        while True:
            # Receive data
            data = await connection.recv()
            
            # Check the first value
            if data[0] == b'JOIN':

                peerid = str(uuid.uuid4())
                # If a peer is joining a cluster, then send the peer our list of peers, as well as the peer's new ID
                await connection.send("JOIN_OK", (self.peers, peerid))

                # Tell all peers that a new peer has joined
                await self._emit(b'NEW', (peerid, connection.addr))

                # This already sends the new request to self.
            elif data[0] == b'NEW':
                if data[1][0] in self.peers.keys():
                    # The peer is already in the cluster
                    # Ignore this request
                    continue
                
                self.peers[data[1][0]] = data[1][1]

                # Log that a new peer is joining
                logger.info(f"New peer {data[1][0]}@{data[1][1][0]}:{data[1][1][1]} has joined the cluster")

        

    
