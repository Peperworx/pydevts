"""
    Implements a basic peer based router implementation.
"""
from ._base import RouterBase
from typing import Optional
import struct
import msgpack

class BasicRouter(RouterBase):

    def __init__(self, owner, **router_config):
        super().__init__(owner, **router_config)
        self.peers = {}

    async def connect_to(self, host: str, port: int):
        """
            Executed when node is attempting to connect to cluster
            Arguments
            - {host}
                Host of the entry node
            - {port}
                Port of the entry node
        """
        pass
    
    async def send(self, target: str, data: bytes):
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """
        for i in self.peers:
            if i[0] == target:
                self.owner.send_to(
                    i[1], i[2], data
                )

    async def _recv_internal(self, name: str, value: bytes):
        print(name, value)
    async def receive(self, data: bytes) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        

        # Unpack header
        header = struct.unpack("BHL", data[:struct.calcsize("BHL")])
        data = data[struct.calcsize("BHL"):]

        # If it is an internal message, treat as such
        if header[0] == 0:
            name = data[:header[1]]
            data = data[header[1]:]
            value = data[:header[2]]
            data = data[header[2]:]

            await self._recv_internal(name.decode(),value)

            return data
        else:
            return data

        