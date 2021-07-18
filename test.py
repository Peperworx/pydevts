from pydevts import Connection
import sys
import trio
import anyio

from Cryptodome.PublicKey import RSA

# Generate RSA keypairs for signing and auth
sign = RSA.generate(2048)
auth = RSA.generate(2048)
print("Keygen complete")
async def main():
    async with await Connection.connect(sign=sign,auth=auth) as conn:
        pass

trio.run(main)