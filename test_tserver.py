from pydevts.protocol.tcp import *
import trio

async def handler(conn: TCPTransport):
    # Echo data back to client
    data = await conn.recv()
    await conn.send(data)

async def main():
    server = TCPTransport(("localhost",0))
    await server.serve(handler)

if __name__ == '__main__':
    trio.run(main)