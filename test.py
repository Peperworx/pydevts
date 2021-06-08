from pydevts.p2p import P2PNode
from pydevts import *
from loguru import logger
import trio
import sys

p = P2PNode()

@logger.catch
async def main():
    
    if len(sys.argv) == 1:
        await p.start()
        await p.run()
    else:
        await p.join(sys.argv[1],sys.argv[2])
    

trio.run(main)