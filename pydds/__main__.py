from .node import *
import trio
import sys
import threading
import struct

async def main():
    n = await Node("localhost",sys.argv[1])

    await n.run()

trio.run(main)