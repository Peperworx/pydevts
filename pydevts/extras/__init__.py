"""
    Pydevts extras
"""

import anyio
from .. import *


async def server_handler_test(client):
    """
        Test custom server handler. Simply echos back recieved data.
    """

    
    async with client:
        
        # Wrap the connection
        client = Connection(client)
        while True:
            # Receive data
            data = await client.receive()

            if data == None:
                break
            
            # Echo data
            await client.send(data)