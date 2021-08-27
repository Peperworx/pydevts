from pydevts.p2p import P2PConnection
import ssl
import anyio
import sys

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("./certs/test.pem", "./certs/test.key")

conn = P2PConnection()

port = 2233

if len(sys.argv) > 1:
    port = int(sys.argv[1])

async def main():
    await conn.connect("localhost", port, usetls=False, verify_key="./certs/test.pem")

    await conn.run()

anyio.run(main)