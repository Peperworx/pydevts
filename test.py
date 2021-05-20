from pydevts.p2p import P2PNode
from pydevts import *
from loguru import logger
import trio

p = P2PNode()

@logger.catch
async def main():
    await p.start()
    await p.run()

trio.run(main)