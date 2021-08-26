from pydevts.host import NodeHost
import anyio
import ssl

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("./certs/test.pem", "./certs/test.key")

host = NodeHost(
    local_host="0.0.0.0",
    local_port=8080,
    ssl_context=context,
)


async def handler(conn):
    while True:
        data = await conn.recv()
        if data == None:
            break
        print(data)
        await conn.send(*data)

async def main():
    await host.run(handler, tls=True)

anyio.run(main)