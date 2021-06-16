from pydevts.protocol.quic import *
import trio
import sys



async def main():
    client = await QUICTransport().connect("google.com",sys.argv[1])
    await client.send(bytes("""GET / HTTP/3\r\n\r\n""".encode()))
    data = await client.recv(0)
    print(data)

if __name__ == '__main__':
    trio.run(main)