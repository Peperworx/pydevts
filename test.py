from pydevts.p2p import P2PNode
from pydevts import *
from loguru import logger
import loguru
import trio
import sys

p = P2PNode()
logger.remove()
logger.add(sys.stderr, level="INFO")
@logger.catch
async def main():
    
    if len(sys.argv) == 1:
        await p.start()
        await p.run()
    else:
        await p.join(sys.argv[1],sys.argv[2])
    

trio.run(main)