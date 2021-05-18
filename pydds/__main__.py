from .p2p import *
import trio
import sys
import threading

p2p = P2PConnection("localhost",int(sys.argv[1]))

@p2p.listen("test")
async def test(ss,data):
    print("message test was recieved!")
    print(data)

@p2p.listen("on_startup")
async def start(c):
    print("Connection Ready")

trio.run(p2p.start)