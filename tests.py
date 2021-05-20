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



async def test_tcp_wrapper():
    try:
        async with anyio.create_task_group() as tg:
            l = await anyio.create_tcp_listener(local_port=0)
            port = l.listeners[0]._raw_socket.getsockname()[1]
            tg.start_soon(l.serve,server_handler_test)
            tg.start_soon(tcp_wrapper_test,port)
    except Cancel:
        pass

