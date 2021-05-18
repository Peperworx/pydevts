from .p2p import *

import sys

p2p = P2PConnection("localhost",int(sys.argv[1]))

@p2p.listen("test")
async def test(ss,data):
    print("message test was recieved!")
    print(data)

p2p.start()