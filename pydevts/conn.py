"""
    Provides a simple anyio TCP connection wrapper.
"""
import anyio
from anyio._core._sockets import SocketStream
import socket
import msgpack
import struct

class Connection:
    wrapped: SocketStream
    raw: socket.socket
    host: str
    port: int

    def __init__(self, wraps: SocketStream):
        self.wrapped = wraps
        self.raw = self.wrapped._raw_socket
        self.host = self.raw.getsockname()[0]
        self.port = self.raw.getsockname()[1]
    
    @classmethod
    async def connect(cls, host: str, port: int):
        return cls(await anyio.connect_tcp(host, port))
    
    async def send(self, data: dict):
        """
            Sends dictionary data over the connection
        """
        await self._send(msgpack.dumps(data))

    async def recv(self) -> dict:
        """
            Receives dictionary data over the connection
        """
        return msgpack.loads(await self._recv())

    async def _send(self, data: bytes):
        """
            Sends raw data over the connection
        """
        data = struct.pack("L",len(data)) + data
        await self.wrapped.send(data)

    async def _recv(self) -> bytes:
        """
            Receives raw data over the connection
        """
        header = struct.unpack("L",self.wrapped.receive(struct.calcsize("L")))
        return await self.wrapped.receive(header[0])