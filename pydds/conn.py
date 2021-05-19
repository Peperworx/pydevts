"""
    This file contains connection wrapper classes
"""
import trio
import struct
import json

class Connection:
    @classmethod
    async def connect(cls, host, port):
        conn = await trio.open_tcp_stream(
            host, port
        )
        
        return cls(conn)

    def __init__(self, conn: trio.SocketStream):
        self.conn = conn
    
    async def recv(self) -> dict:
        """
            Recieves dictionary data from the connection
        """
        offset = struct.calcsize("L")
        recsize = await self.conn.receive_some(offset)
        if len(recsize) < offset:
            return {}
        size = struct.unpack("L",recsize)[0]
        data = (await self.conn.receive_some(size)).decode()
        data = json.loads(data)
        return data
    
    async def send(self, data: dict):
        """
            Sends JSON dictionary data over the connection
        """
        # Pack the data
        packed = await self._pack(data)

        # Send the data
        await self.conn.send_all(packed)
    

    
    async def _pack(self, data: dict) -> bytes:
        """
            Packs a JSON dictionary into a message for sending over TCP
        """

        # Dump the json
        data = json.dumps(data, separators=(',',':')).encode()

        # Grab the length
        data_len = len(data)

        # Pack and return data
        return struct.pack("L",data_len)+data
    
    async def aclose(self):
        return await self.conn.aclose()