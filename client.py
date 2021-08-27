from pydevts.conn import NodeConnection
import anyio

conn = NodeConnection("certs/test.pem")

async def main():
    handle = await conn.connect("localhost",8080)
    
    await conn.send(handle, "Hello World!", b"testdata")

    data = await conn.recv(handle)
    print(data)
    await conn.close()

anyio.run(main)