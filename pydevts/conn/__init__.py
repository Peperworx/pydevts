"""
    Provides basic TCP message wrapper for managing connections to multiple nodes.

    NOTE: This does *not* function as you would expect a TCP connection to work.
          It is a wrapper around TCP that implements a message protocol.
          Messages are sent with a "name" and some "data". Streams *can* be used, but they are implemented as a specific message type.
"""
# Logging
from ..logger import logger as logger

# UUID for random connection IDs
from uuid import uuid4

# For starting connections
from anyio import connect_tcp

# Classes for type hints
from anyio.streams.tls import TLSStream
from anyio.abc._sockets import SocketStream
from typing import Optional, Union

# Data serialization
import msgpack
import struct

class NodeConnection:
    
    connections: dict[str, Union[TLSStream, SocketStream]]

    def __init__(self: "NodeConnection"):
        """Message wrapper for handling multiple TCP connections.

        Args:
            self (NodeConnection): [description]
        """

        # Initialize dictionary of connections
        self.connections = dict()
        
    @logger.catch
    async def connect(self: "NodeConnection", remote_host: str, remote_port: int, usetls: bool = False) -> str:
        """Connect to remote TCP host

        Args:
            self (NodeConnection)
            remote_host (str): The host of the target
            remote_port (int): The port of the target
            usetls (bool, optional): If the connection should use TLS. Defaults to False.

        Returns:
            str: The locally used ID for the remote host. Used when sending data to the host.
        """

        # Create a new connection, if using TLS, pass that as well
        connection = await connect_tcp(remote_host, remote_port, tls=usetls)


        # Generate a new ID for the remote host
        remote_id = str(uuid4())

        # While the remote id is in the list of connections, generate a new one
        while remote_id in self.connections.keys():
            # This should never execute, but we use it just in case
            remote_id = str(uuid4())
        
        # Add the connection to the list of connections
        self.connections[remote_id] = connection

        # Return the ID
        return remote_id

    @logger.catch
    async def disconnect(self: "NodeConnection", remote_id: str):
        """Disconnect from remote TCP host

        Args:
            self (NodeConnection)
            remote_id (str): The ID of the remote host.
        """
        
        # Make sure the ID is in the list of connections
        if remote_id not in self.connections.keys():
            raise ValueError(f'No connection to "{remote_id}"')
        
        # Close the connection
        await self.connections[remote_id].aclose()

        # Remove the connection from the list of connections
        del self.connections[remote_id]

    @logger.catch
    async def close(self: "NodeConnection"):
        """Close all connections"""

        # Close all connections
        for connection in self.connections.values():
            await connection.aclose()

        # Clear the list of connections
        self.connections = dict()
    
    @logger.catch
    async def send(self: "NodeConnection", remote_id: str, name: str, data: bytes):
        """Send a message to a remote host
        
        Args:
            self (NodeConnection)
            remote_id (str): The ID of the remote host.
            name (str): The name of the message.
            data (bytes): The data to send.
        """

        # Generate msgpack data
        data = msgpack.packb((name, data))

        # Generate length header
        length = struct.pack('!I', len(data))

        # Send the message
        await self.connections[remote_id].send_all(length + data)
        
    
    @logger.catch
    async def recv(self: "NodeConnection", remote_id: str) -> tuple[str, bytes]:
        """Receive a message from a remote host

        Args:
            self (NodeConnection)
            remote_id (str): The ID of the remote host to wait on
        
        Returns:
            tuple[str, bytes]: The name and data of the message
        """

        # Receive the length header
        length = await self.connections[remote_id].receive(struct.calcsize('!I'))

        # Unpack length header
        length = struct.unpack('!I', length)[0]

        # Receive the data
        data = await self.connections[remote_id].receive(length)

        # Unpack data
        data = msgpack.unpackb(data)

        # Validate that data returned is a tuple of the correct size
        if data.isinstance(tuple) and len(data) != 2:
            raise ValueError('Remote host returned invalid data')


        # Return the name and data
        return data
    
    @logger.catch
    async def emit(self: "NodeConnection", name: str, data: bytes):
        """Send a message to all connected nodes

        Args:
            self (NodeConnection)
            name (str): The name of the message.
            data (bytes): The data to send.
        """

        # Generate msgpack data
        data = msgpack.packb((name, data))

        # Generate length header
        length = struct.pack('!I', len(data))

        # Send the message
        for connection in self.connections.values():
            await connection.send(length + data)
        