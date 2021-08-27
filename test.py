from pydevts.node import _Node
from pydevts.auth.rsa import AuthRSA
import anyio
import sys
from loguru import logger


port = 2233

if len(sys.argv) > 1:
    port = int(sys.argv[1])

# Load RSA keys from files
with open(f"./certs/{sys.argv[2]}", "rb") as f:
    privkey = f.read()

with open(f"./certs/{sys.argv[2]}.pub", "rb") as f:
    pubkey = f.read()

# Create RSA auth method
auth_method = AuthRSA(pubkey, privkey)

node = _Node(('localhost', port),auth_method=auth_method)


async def on_start():
    print(node.conn.router.peers)

node.bind_start(on_start)

@logger.catch
async def main():
    await node.run()

if __name__ == "__main__":
    anyio.run(main)
