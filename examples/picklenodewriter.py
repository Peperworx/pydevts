"""
    Code in this file works in conjunction with code in picklenode.py to show how different nodes can work together.
    This file contains a node that simply writes to a file every time data is replicated
"""

from pydds import Node, Connection

import pickle
import trio
import sys
import logging
import base64

class PickleWriterNode(Node):
    async def on_replicate(self, request, data: dict):
        if data.get("type") != "picklenode":
            return
        fs = await trio.open_file("./pickleoutput.txt","a")
        await fs.write(str(pickle.loads(base64.b64decode(data["value"]))))
        await fs.write("\n")
        await fs.aclose()


TESTNODE = PickleWriterNode(host="localhost",port=sys.argv[1])



async def main():
    await TESTNODE.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    trio.run(main)