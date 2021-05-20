"""
    Implements custom TCP connection wrappers.
"""
import anyio

from .errors import *

# We need some secret stuff :)
from anyio._core._sockets import SocketStream

# Standard imports
import json
import struct
import socket
import base64
import typing



class Connection:
    """
        Anyio TCP connection wrapper.
    """

    wrapped: SocketStream
    raw: socket.socket
    host: int
    port: int

    def __init__(self, wrapped: SocketStream):
        """
            Wraps an anyio SocketStream.
        """
        
        self.wrapped = wrapped
        self.raw = wrapped._raw_socket
        self.host = self.raw.getsockname()[0]
        self.port = self.raw.getsockname()[1]
    

    async def send(self, data: dict) -> typing.Literal[None]:
        """
            Sends JSON encodable dictionary over socket.
        """
        
        # Pack data
        packed = self._pack(data)

        # Send data
        await self.wrapped.send(packed)
    
    async def recv(self) -> dict:
        """
            Recieves a JSON encoded dictionary over socket.
        """

        # Recieve the header
        header = await self.wrapped.receive(struct.calcsize('L'))

        # Check the header length
        if len(header) < struct.calcsize('L'):
            # If it is to short, raise an error
            raise HeaderParseError("Received a smaller header than expected")
        
        # Unpack the data
        header = struct.unpack('L', header)

        # Recieve the rest of the data
        data = await self.wrapped.receive(header[0])

        # Decode the data
        decoded = base64.b64decode(data).decode()

        # Load the data and return
        return json.loads(decoded)

    @staticmethod
    def _pack(data: dict) -> bytearray:
        """
            Packs a JSON encodable dictionary into a bytearray.
        """

        # Initialize return value
        ret = bytearray()

        # Dump JSON
        dumped = json.dumps(data,separators=(",",":"))

        # Encode JSON
        encoded = base64.b64encode(dumped.encode())

        # Grab the length
        data_len = len(dumped)

        # Add the packed length
        ret += struct.pack("L",data_len)

        # Add the data
        ret += encoded

        # Return
        return ret
    @staticmethod
    def _unpack(data: bytearray) -> dict:
        """
            Unpacks encoded JSON into a dictionary. Inverse of _pack
        """

        # Grab the data length
        data_len = struct.unpack("L",data[:struct.calcsize("L")])

        # Skip header
        content = data[struct.calcsize("L"):]

        # Decode
        decoded = base64.b64decode(content[:data_len]).decode()

        # Parse and return
        return json.loads(decoded)