from .node import *
from .p2p import *
import trio
import sys




async def main():
    n = Node("localhost",sys.argv[1])
    
    
    await n.run()

trio.run(main)