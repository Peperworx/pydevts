from pydevts.protocol.tcp import *
import trio

async def handler(conn: TCPConnection):
    data = await conn.recv(1024)
    print(data)

async def main():
    server = TCPTransport()
    await server.serve(handler,"localhost")

if __name__ == '__main__':
    trio.run(main)