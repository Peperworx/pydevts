import anyio
from pydevts.event import P2PEventSystem
import sys


port = sys.argv[1]


evt = P2PEventSystem()

async def test_bcast(node, data):
    print(f"Received broadcast data from {node}: b'{str(data)}'")
    await evt.send_to(node, "test_response", data)

async def test_response(node, data):
    print(f"Received response data from {node}: b'{str(data)}'")


evt.register_event_handler("test_bcast", test_bcast)
evt.register_event_handler("test_response", test_response)

async def on_start():
    print(evt.server.port)
    await evt.emit('test_bcast', b'Hello World!')

async def data_handler(node: str, data: bytes):
    print(f"Received b'{str(data)}' from {node}")

async def main():

    # Connect to the server
    await evt.connect('127.0.0.1', port)

    # Create task group
    async with anyio.create_task_group() as tg:
        # Start the server
        await tg.start(evt.run)

        # Start the on_start function
        tg.start_soon(on_start)
    
anyio.run(main)