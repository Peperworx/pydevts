"""
    Code in this file works in conjunction with code in picklenode.py to show how different nodes can work together.
    This file contains a node that simply writes to a file every time data is replicated
"""

from pydevts import *

import trio
import sys
import logging
import base64

class PickleWriterNode(Node):
    
    async def on_replicate(self, data: dict):
        if data.get("type") != "picklenode":
            return
        fs = await trio.open_file("./pickleoutput.txt","wb+")
        await fs.write(base64.b64decode(data["value"]))
        await fs.aclose()


TESTNODE = PickleWriterNode(host="localhost",port=sys.argv[1])



async def main():
    await TESTNODE.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    trio.run(main)