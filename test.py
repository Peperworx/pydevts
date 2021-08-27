from pydevts.node import _Node
import ssl
import anyio
import sys


port = 2233

if len(sys.argv) > 1:
    port = int(sys.argv[1])

node = _Node(('localhost', port))


async def on_start():
    print(node.conn.router.peers)

node.bind_start(on_start)


async def main():
    await node.run()

if __name__ == "__main__":
    anyio.run(main)
