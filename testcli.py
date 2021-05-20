import pydevts
import anyio
import trio
import sys

async def main():
    s = await anyio.connect_tcp("localhost",sys.argv[1])
    c = pydevts.Connection(s)
    await c.send({
        "test":"value"
    })

trio.run(main)