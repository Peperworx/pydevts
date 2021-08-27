from pydevts.pub import Node
from pydevts.auth.rsa import AuthRSA
import sys


# Gather port from command line
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


# Initialize node
node = Node("localhost", port, auth_method=auth_method)



@node.on("test_bcast")
async def test_bcast(from_node: str, name: str, data: bytes):
    print(f"{from_node} sent {name} with data {data} over broadcast")

    node.send(from_node, "bcase_response", data)

@node.on("bcast_response")
async def bcast_response(from_node: str, name: str, data: bytes):
    print(f"{from_node} sent {name} with data {data} as response to broadcast")

@node.on_sys("startup")
async def startup():
    print("Node is starting up")
    node.emit('test_bcast', b"Hello World")

if __name__ == "__main__":
    node.run()