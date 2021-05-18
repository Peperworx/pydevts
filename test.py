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
    await n.emit("test_event","hello, world!")
    

@n.on("test_event")
async def test_event(request, data):
    print(data)
    

async def main():
    
    async with trio.open_nursery() as nursery:
        nursery.start_soon(n.run)
        c = Config()
        c.bind = [f"localhost:{sys.argv[2]}"]
        nursery.start_soon(serve,app,c)


if __name__ == '__main__':
    trio.run(main)