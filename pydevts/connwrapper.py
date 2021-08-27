"""Implements a basic connection wrapper
"""
# Typeh ints
from anyio.abc._sockets import SocketStream

# Data serialization
import msgpack
import struct


class _WrappedConnection:
    _connection: SocketStream
    addr: tuple[str, int]

    def __init__(self: '_WrappedConnection', connection: SocketStream):
        """Wraps a socket stream to provide a message based interface

        Args:
            self (_WrappedConnection)
            connection (SocketStream): The wrapped connection
        """
        
        self._connection = connection

        self.addr = connection._raw_socket.getpeername()

    
    async def close(self):
        """Closes the connection
        """
        await self._connection.aclose()

    
    async def send(self: '_WrappedConnection', name: str, data: bytes):
        """Sends a message over the connection
        
        Args:
            self (_WrappedConnection)
            name (str): The name of the message
            data (bytes): The data to send
        """
        
        # Generate msgpack data
        data = msgpack.packb((name, data))

        # Generate length header
        length = struct.pack('!I', len(data))

        # Send the message
        await self._connection.send(length + data)
    
    async def recv(self: '_WrappedConnection') -> tuple[str, bytes]:
        """Receives a message over the connection
        
        Returns:
            tuple[str, bytes]: The name and data of the message
        """

        # Receive the length header
        length = await self._connection.receive(struct.calcsize('!I'))

        # Unpack length header
        length = struct.unpack('!I', length)[0]

        # Receive the data
        data = await self._connection.receive(length)

        # Unpack data
        data = msgpack.unpackb(data)

        # Validate that the data returned is a tuple of the correct size
        if not isinstance(data, list) or len(data) != 2:
            raise ValueError('Remote client returned invalid data')
        return data