"""
    Basic PYDEVTS auth server
"""
from pydevts.server import Server
import trio


from Cryptodome.PublicKey import RSA

# Generate RSA keypairs for signing and auth
sign = RSA.generate(2048)
auth = RSA.generate(2048)
print("Keygen complete")


async def _handler(connection):
    while True:
        data = connection.receive(1024)
        if not data:
            break
        print(data)
async def main():
    await Server.serve(_handler, auth = auth, sign = sign)

trio.run(main)