from pydevts import P2PConnection
import sys
import trio
import anyio

async def main():
    async with P2PConnection(entry=("localhost",sys.argv[1])) as conn:
        pass

trio.run(main)