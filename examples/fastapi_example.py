import trio
from pydevts.node import *
from fastapi import FastAPI
from hypercorn.trio import serve
from hypercorn.config import Config
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

n = DBNode(host='localhost', port=sys.argv[1])

app = FastAPI()

@app.get("/")
async def index():
    conn = await n.send(n.conn.nid,"test_event","hello, world!")
    data = await conn.recv()
    print(data)
    await n.emit("test_broadcast",data)


@app.get("/store")
async def store():
    return n.__dict__()

@app.get("/set/{name}/{value}")
async def set(name: str, value: str):
    await n.set(name,value)

@n.on("test_event")
async def test_event(request, data):
    await request.send({
        "message":"test",
        "data":data
    })

@n.on("test_broadcast")
async def test_broadcast(request, data):
    print("From Broadcast")
    print(data)
    


async def main():
    
    async with trio.open_nursery() as nursery:
        nursery.start_soon(n.run)
        c = Config()
        c.bind = [f"localhost:{sys.argv[2]}"]
        nursery.start_soon(serve,app,c)


if __name__ == '__main__':
    trio.run(main)