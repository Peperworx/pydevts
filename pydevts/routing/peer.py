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
from ..auth._base import _Auth

# Node hosts and connections
from ..host import NodeHost
from ..conn import NodeConnection

# Auth
from ..auth.noauth import AuthNone

class PeerRouter(_Router):
    """Peer-based routing system
    """

    host: str
    port: int
    host_addr: tuple[str, int]
    connection: NodeConnection
    entry: str
    node_id: str
    peers: dict[str, tuple[str, int]]
    auth_method: _Auth
    data_handler: Callable[[str, bytes],None]

    def __init__(self):
        """Initialize the router
        """


        # Set default values
        self.peers = dict()
        self.data_handler = None
    
    async def enter(self, host: str, port: int, host_addr: tuple[str, int], auth_method: _Auth = AuthNone()):
        """Enters a cluster

        Args:
            host (str): The entry host of the cluster
            port (int): The entry port of the cluster
            host_addr (tuple[str, int]): The address that we are hosting on
            auth_method (_Auth): The authentication method to be used
        """

        # Save values passed
        self.host = host
        self.port = port
        self.host_addr = host_addr
        self.auth_method = auth_method

        # Create the connection
        self.connection = NodeConnection(auth_method=self.auth_method)

        # Wrap with try, except so that we can detect if the connection fails
        try:
            # Connect to the entry node
            self.entry = await self.connection.connect(host, port)

            # Tell entry that we have joined
            await self.connection.send(self.entry, 'JOIN', (host_addr,))

            # Await our connection info
            conn_info = await self.connection.recv(self.entry)
            # Check if we have joined successfully
            if conn_info[0] != 'JOIN_OK':
                raise ConnectionError("Failed to join cluster")
            
            # If not, set our peer list
            self.peers = conn_info[1][0]

            # Add our entry node
            self.peers[conn_info[1][2]] = (host, port)

            # Set our nodeId
            self.node_id = conn_info[1][1]

            # Log that we have joined
            logger.info(f"Joined cluster via entry node {conn_info[1][2]}@{host}:{port}")

        except OSError as e:
            logger.warning(f"Unable to connect to cluster at {host}:{port}. Starting new cluster")
            self.node_id = str(uuid.uuid4())
        
    
    async def send_to(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        if node_id == self.node_id:
            # If we are sending to ourselves, just handle it
            await self.data_handler(self.node_id, data)
            return

        # Open connection
        connection = await self.connection.connect(self.peers[node_id][0], self.peers[node_id][1])

        # Send data
        await self.connection.send(connection, "DATA", (self.node_id, data))

        # Clean all connections that have not been used in 60 seconds
        await self.connection.clean()
    
    async def emit(self, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            data (bytes): The data to emit
        """

        # Delegate to subfunction
        await self._emit('DATA', (self.node_id, data))

    
    async def _emit(self, name: str, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            name (str): The name of the event
            data (bytes): The data to emit
        """
        remove = []
        # Send to all peers
        for peer in self.peers.copy().keys():
            try:
                handle = await self.connection.connect(self.peers[peer][0], self.peers[peer][1])
                await self.connection.send(handle, name, data)
                await self.connection.clean() # We use clean instead of disconnect to maintain a cache of connections
            except OSError:
                remove.append(peer)
        
        # Remove dead peers
        for peer in remove:
            del self.peers[peer]
        
        # Send to self
        handle = await self.connection.connect(*self.host_addr)
        await self.connection.send(handle, name, data)
        await self.connection.clean()
    
    async def register_handler(self, datahandler: Callable[[str, bytes],None]):
        """Registers the data handler
        
        Args:
            datahandler (Callable[[bytes],None]): The data handler
        """

        self.data_handler = datahandler

    async def on_connection(self, connection: _WrappedConnection):
        """Handles a new connection
        
        Args:
            connection (connwrapper._WrappedConnection): The connection to handle
        """

        while True:
            # Receive data
            data = await connection.recv()
            
            # Check the first value
            if data[0] == 'JOIN':

                peerid = str(uuid.uuid4())
                # If a peer is joining a cluster, then send the peer our list of peers, as well as the peer's new ID
                await connection.send("JOIN_OK", (self.peers, peerid, self.node_id))
                
                # Tell all peers that a new peer has joined
                await self._emit('NEW', (peerid, connection.addr, data[1][0]))
                
                # This already sends the new request to self.
            elif data[0] == 'NEW':
                if data[1][0] in self.peers.keys():
                    # The peer is already in the cluster
                    # Ignore this request
                    continue
                host = data[1][1][0]
                port = data[1][2][1]
                self.peers[data[1][0]] = (host, port)

                # Log that a new peer is joining
                logger.info(f"New peer {data[1][0]}@{data[1][1][0]}:{data[1][2][1]} has joined the cluster")
            elif data[0] == 'DATA':
                # Handle data
                if self.data_handler:
                    await self.data_handler(data[1][0], data[1][1])
        

    
