from pydevts.node import _Node
from pydevts.auth.rsa import AuthRSA
import ssl
import anyio
import sys


port = 2233

if len(sys.argv) > 1:
    port = int(sys.argv[1])

# Load RSA keys from files
with open("./certs/id", "rb") as f:
    privkey = f.read()

with open("./certs/id.pub", "rb") as f:
    pubkey = f.read()

# Create RSA auth method
auth_method = AuthRSA(privkey, pubkey)

node = _Node(('localhost', port))


async def on_start():
    print(node.conn.router.peers)

node.bind_start(on_start)


async def main():
    await node.run()

if __name__ == "__main__":
    anyio.run(main)
