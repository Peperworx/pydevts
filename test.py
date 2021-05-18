import trio
from pydds.node import *
from fastapi import FastAPI
from hypercorn.trio import serve
from hypercorn.config import Config
import sys

n = DBNode('localhost', sys.argv[1])

app = FastAPI()

@app.get("/")
async def index():
    await n.conn.broadcast("test event",{})
    return n.conn.peers

@app.get("/setlocal/{name}/{data}")
async def setlocal(name: str, data: str):
    await n.__setitem__(name, data)

@app.get("/getlocal/{name}")
async def getlocal(name: str):
    return await n[name]

@app.get("/store")
async def getstore():
    return n.store
async def main():
    
    async with trio.open_nursery() as nursery:
        nursery.start_soon(n.run)
        c = Config()
        c.bind = [f"localhost:{sys.argv[2]}"]
        nursery.start_soon(serve,app,c)


if __name__ == '__main__':
    trio.run(main)