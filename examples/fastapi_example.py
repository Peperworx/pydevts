import asyncio
from pydevts.node import *
from fastapi import FastAPI
from hypercorn.asyncio import serve
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
async def test_event(conn, data):
    await conn.send({
        "message":"test",
        "data":data
    })

@n.on("test_broadcast")
async def test_broadcast(data):
    print("From Broadcast")
    print(data)
    


async def main():
    t1 = asyncio.create_task(n.run())
    c = Config()
    c.bind = [f"localhost:{sys.argv[2]}"]
    t2 = asyncio.create_task(serve(app, c))
    
    await t1
    await t2


if __name__ == '__main__':
    asyncio.run(main())