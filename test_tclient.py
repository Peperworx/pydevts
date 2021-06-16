from pydevts.protocol.tcp import *
import trio
import sys



async def main():
    client = await TCPTransport().connect("localhost",sys.argv[1])
    await client.send(bytes(sys.argv[2].encode()))

if __name__ == '__main__':
    trio.run(main)