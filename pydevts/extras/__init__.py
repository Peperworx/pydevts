"""
    Pydevts extras
"""

import anyio
from .. import *

class Cancel(Exception):
    """
        Exception
    """
    ...

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


async def tcp_wrapper_test(port):
    """
        Test client for test server. Takes a tcp port as an argument
    """
    
    # Create a connection
    async with await anyio.connect_tcp("localhost", port) as conn:
        # Wrap the connection
        connw = Connection(conn)
        # Send
        tosend = {"test":"val"}
        await connw.send(tosend)
        # Receive
        recv = await connw.receive()
        # Assert that we got back the same
        assert tosend == recv
    # Basically return
    raise Cancel()