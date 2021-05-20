"""
    Provides wrapper classes for anyio TCP requests.
"""

import anyio
import struct
import binascii
import json

class Connection:
    def __init__(self, wrapped):
        """
            Anyio TCP wrapper that can send JSON encodable dictionaries.
        """
        self.wrapped = wrapped

        # Calculate size of 'L'
        self.offset = struct.calcsize('L')
    
    async def receive(self) -> dict:
        """
            Receive JSON dictionary over TCP.
        """

        try:
            # Receive the header
            header = await self.wrapped.receive(self.offset)
        except anyio.EndOfStream:
            return None
        # If it is less than the required size, return None
        if len(header) < self.offset:
            return None
        
        
        # Parse the header
        headerp = struct.unpack('L',header)
        
        # Read the data
        data = await self.wrapped.receive(headerp[0])
        
        try:
            # Parse the data
            parsed = json.loads(data.decode())
        except json.JSONDecodeError:
            # If it fails to decode, return None
            return None
        
        # Return
        return parsed
    
    async def send(self, data: dict):
        """
            Send JSON parsable data to the peer.
        """
        
        # Dump the data. Let exceptions be raised
        dumped = json.dumps(data)

        # Grab the length
        data_len = len(dumped)

        # Encode the header
        header = struct.pack('L', data_len)

        # Prepare the payload
        payload = header + dumped.encode()
        
        # Send the data
        await self.wrapped.send(payload)
        