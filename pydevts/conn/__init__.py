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
from ..auth._base import _Auth

# Data serialization
import msgpack
import struct

# Encryption and authentication
import ssl
from ..auth.noauth import AuthNone


class NodeConnection:
    
    connections: dict[str, Union[TLSStream, SocketStream]]
    verify_key: Optional[str]
    auth_method: Optional[_Auth]

    def __init__(self: "NodeConnection", verify_key: str = None, auth_method: _Auth = AuthNone()):
        """Message wrapper for handling multiple TCP connections.

        Args:
            self (NodeConnection): [description]
            verify_key (str): The key to be used to verify untrusted connections.
            auth_method (_Auth): The authentication method to be used
        """

        # Set verify key
        self.verify_key = verify_key

        # Initialize dictionary of connections
        self.connections = dict()

        # Set out authentication method
        self.auth_method = auth_method
        
    
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

        # If we have a verify key, use it for untrusted connections
        if usetls and self.verify_key:
            # Create ssl context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

            # Load the verify key
            context.load_verify_locations(cafile=self.verify_key)

            # Create a new connection
            connection = await connect_tcp(remote_host, remote_port, ssl_context=context)
        else:
            # Create a new connection, if using TLS, pass that as well
            connection = await connect_tcp(remote_host, remote_port, tls=usetls)

        # Run authentication
        if self.auth_method:
            # Execute handshake
            await self.auth_method.handshake(connection)

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

    
    async def close(self: "NodeConnection"):
        """Close all connections"""

        # Close all connections
        for connection in self.connections.values():
            await connection.aclose()
        
        # Clear the list of connections
        self.connections = dict()
    
    
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
        await self.connections[remote_id].send(length + data)
        
    
    
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
        if not isinstance(data, list) or len(data) != 2:
            raise ValueError('Remote host returned invalid data')


        # Return the name and data
        return data
    
    
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
        