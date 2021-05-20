"""
    Unittests for pydevts.
"""


# Import everything from pydevts
from pydevts import *

# Also import extras
from pydevts.extras import *


import anyio
import pytest


pytestmark = pytest.mark.anyio

class Cancel(Exception):
    """
        Exception
    """
    ...

async def test_tcp_wrapper():
    
    async def tcp_wrapper_test(listener, tg):
        port = listener.listeners[0]._raw_socket.getsockname()[1]
        
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

        
    try:
        async with anyio.create_task_group() as tg:
            l = await anyio.create_tcp_listener(local_port=0)
            tg.start_soon(l.serve,server_handler_test)
            tg.start_soon(tcp_wrapper_test,l, tg)
    except Cancel:
        pass
