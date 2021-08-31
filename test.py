import anyio
from pydevts.pub import Node
import sys


port = sys.argv[1]


app = Node()

@app.on('test_bcast')
async def test_bcast(node: str, data: bytes):

    print(f"Received broadcast from {node} with data b'{str(data)}'")

    await app.send(node, 'test_resp', data)

@app.on('test_resp')
async def test_resp(node: str, data: bytes):
    print(f"Received response from {node} with data b'{str(data)}'")

@app.on_sys('startup')
async def startup():
    print("Started")
    await app.emit("test_bcast", b"Hello, World!")

async def main():
    # Connect to the server
    await app.connect('127.0.0.1', port)

    # Run the node
    await app.run()
    
anyio.run(main)