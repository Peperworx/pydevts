from pydevts.protocol.tcp import *
import trio
import sys



async def main():
    tt = TCPTransport(("localhost",sys.argv[1]))
    async with tt as c:
        await c.send(bytes(sys.argv[2].encode()))
        print(await c.recv())
    
    # Now without context manager
    await tt.open()

    await tt.send(bytes(sys.argv[2].encode()))
    print(await tt.recv())

    await tt.close()


if __name__ == '__main__':
    trio.run(main)