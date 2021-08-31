import anyio
from pydevts.p2p import P2PConnection
import sys


port = sys.argv[1]

async def on_start(conn: P2PConnection):
    # Send data on start
    print(conn.server.port)
    await conn.emit(b"I am here!")

async def data_handler(node: str, data: bytes):
    print(f"Received b'{str(data)}' from {node}")

async def main():
    # Create a connection
    conn = P2PConnection()

    # Connect to the server
    await conn.connect('127.0.0.1', port)

    # Register data handler
    conn.register_data_handler(data_handler)

    # Create task group
    async with anyio.create_task_group() as tg:
        # Start the server
        await tg.start(conn.run)

        # Start the on_start function
        tg.start_soon(on_start, conn)
    
anyio.run(main)