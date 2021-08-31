"""
    Basic peer-based routing system
"""

# Logging
from ..logger import logger


# Unique IDs
import uuid

# Router parent
from ._base import _Router

# Type Hints
from ..proto import _Client, _Conn, _Server
from typing import Callable

# Clients and servers
from ..conn import MultiClientCache

# TCP server is default
from ..proto import TCPProto

# Serialization
from ..msg import MsgNum
import msgpack


class PeerRouter(_Router):
    """Peer-based routing system
    """

    entry_addr: tuple[str, int]
    host_addr: tuple[str, int]
    connections: MultiClientCache
    peers: dict[str, tuple[str, int]]
    data_handler: Callable[[bytes],None]
    entry: str
    node_id: str


    def __init__(self, protocol: tuple[_Client, _Conn, _Server] = TCPProto):
        """Initialize the router
        """

        
        # Set default values
        self.peers = dict()
        self.data_handler = None

        # Create MultiConnectionCache
        self.connections = MultiClientCache(proto=protocol)

    async def enter(self, entry_addr: tuple[str, int], host_addr: tuple[str, int]):
        """Enters a cluster

        Args:
            entry_addr (tuple[str, int]): The address of the entry node.
            host_addr (tuple[str, int]): The address that we are hosting on
        """

        # Save entry address and host address
        self.entry_addr = entry_addr
        self.host_addr = host_addr

        # Wrap with try-except so we can detect if the connection fails
        try:
            # Connect to the entry node
            self.entry = await self.connections.connect(*entry_addr)

            # Tell the entry node we have joined
            await self.connections.send(
                self.entry,
                MsgNum.dumps(0, msgpack.packb(
                    (host_addr,)
                ))
            )

            # Await out connection info
            conn_info = await self.connections.recv(self.entry)
            
            # Unpack connection info
            data_type, data = MsgNum.loads(conn_info)

            # Verify that we have joined successfully
            if data_type != 0:
                raise ConnectionError("Failed to join cluster")
            
            # Unpack data
            data = msgpack.unpackb(data)

            # Save peer list
            self.peers = data[0]

            # Save our ID
            self.node_id = data[1]

            # Save the entry node ID in peers
            self.peers[data[2]] = self.entry_addr

            # Log that we have joined
            logger.info(f"Joined cluster via entry node {data[2]}@{self.entry_addr[0]}:{self.entry_addr[1]}")


        except OSError as e:
            logger.warning(f"Unable to connect to cluster at {self.entry_addr[0]}:{self.entry_addr[1]}. Starting new cluster")
            self.node_id = str(uuid.uuid4())

        
    
    async def send_to(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID of the node to send to
            data (bytes): The data to send
        """

        raise NotImplementedError("This is an abstract class")
    
    async def emit(self, data: bytes):
        """Emits data to all connected nodes
        
        Args:
            data (bytes): The data to emit
        """

        raise NotImplementedError("This is an abstract class")
    


    
    async def _emit(self, data: bytes) -> None:
        """Internal function to emit data to all connected nodes

        Args:
            data (bytes): The data to emit
        """

        # List of peers to remove
        remove = []

        # Send to all peers
        for peer in self.peers.copy().keys():
            try:
                # Connect
                handle = await self.connections.connect(self.peers[peer][0], self.peers[peer][1])

                # Send
                await self.connections.send(handle, data)
                
                # Clean up connections
                await self.connections.clean()
            except OSError:
                # Remove peer
                remove.append(peer)
        
        # Remove dead peers
        for peer in remove:
            del self.peers[peer]
        
        # Handle it ourselves
        await self._on_data(data)




    async def register_data_handler(self, data_handler: Callable[[bytes],None]):
        """Registers the data handler
        
        Args:
            data_handler (Callable[[bytes],None]): The handler which is called when data is received.
        """

        # Register the data handler
        self.data_handler = data_handler
    


    async def _on_data(self, data: bytes):
        """Handles data received

        Args:
            data (bytes): The data received
        """

        # Unpack type
        data_type, data = MsgNum.loads(data)

        # Check the type
        if data_type == 0: # Join

            # Generate ID for new peer
            peer_id = str(uuid.uuid4())

            # Tell the peer our peers, its ID, and our ID
            await self.connections.send(
                MsgNum.dumps(
                    1,
                    msgpack.packb(
                        (
                            self.peers,
                            peer_id,
                            self.node_id
                        )
                    )
                )
            )


    async def on_connection(self, connection: _Conn):
        """Handles a new connection
        
        Args:
            connection (_Conn): The connection to handle
        """

        while True:
            # Receive data
            data = await connection.recv()

            # Handle data
            await self._on_data(data)

            
