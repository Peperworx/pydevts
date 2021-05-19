"""
    This example shows how you can implement a custom node type to store a pickled object
"""

from pydds import Node, Connection

import pickle
import trio
import sys
import logging
import base64

class PickleNode(Node):
    def __init__(self):
        self.stored = object
    

    def get(self):
        return self.stored

    async def set(self,v):
        await self.conn.broadcast("on_replicate",{
            "type":"picklenode",
            "value":base64.b64encode(pickle.dumps(v)).decode()
        })

        self.stored = v

    async def on_startup(self):
        """
            Function called when the node successfully connects to the cluster
        """

        self._info = {
            "id":self.conn.nid,
            "keys_known":[],
            "init":False
        }
        
        
        if len(self.conn.peers) == 0:
            self._info["init"] = True
            return

        n = await self.find_node(lambda a: a["init"]==True)
        
        # Create connection to this peer
        cn: Connection = await Connection.connect(n["host"],n["port"])

        # Send a message
        await cn.send({
            "type":"message",
            "from":self.conn.nid,
            "port":self.conn.server.socket.getsockname()[1],
            "name":"on_fetch",
            "data":{
                "type":"picklenode",
                "id":self.conn.nid
            }
        })
        

    ##############################
    #      Data Replication
    ##############################

    async def on_replicate(self, request, data: dict):
        """
            Function called when data needs to be replicated
        """
        if data.get("type") != "picklenode":
            return
        self.stored = pickle.loads(base64.b64decode(data["value"]))
    


    async def on_fetch(self, request, data: dict):
        """
            Function called when a node needs to read a value from other nodes.
        """
        if data.get("type") != "picklenode":
            return

        await self.conn.sendto(
            data["id"],
            "on_replicate",
            {
                "type":"picklenode",
                "value":base64.b64encode(pickle.dumps(self.stored)).decode()
            }
        )

TESTNODE = PickleNode(host="localhost",port=sys.argv[1])

async def loop():
    await TESTNODE.set(int(0))
    while True:
        print(TESTNODE.get())
        await trio.sleep(1)
        if len(sys.argv) >= 3 and sys.argv[2] == "w":
            await TESTNODE.set(TESTNODE.get()+1)

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(TESTNODE.run)
        nursery.start_soon(loop)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    trio.run(main)