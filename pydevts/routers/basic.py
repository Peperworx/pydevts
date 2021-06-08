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
        pass

    async def receive(self, data: bytes) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        

        # Unpack header
        header = struct.unpack("B", data[:struct.calcsize("B")])
        data = data[struct.calcsize("B"):]

        # If it is an internal message, treat as such
        if header[0] == 0:
            message = msgpack.loads(data)
            self._recv_internal(message)
        else:
            return data

        