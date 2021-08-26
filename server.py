from pydevts.host import NodeHost
import anyio

host = NodeHost(
    local_host="0.0.0.0",
    local_port=8080,
    keypair=("./certs/test.pem", "./certs/test.key")
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