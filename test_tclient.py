from pydevts.protocol.quic import *
import trio
import sys



async def main():
    tt = QUICTransport(("google.com",sys.argv[1]))

    # With context manager
    async with tt as c:
        await c.send(bytes(sys.argv[2].encode()))
        print(await c.recv())
    
    # Now without context manager
    await tt.open()

    await tt.send(bytes(sys.argv[2].encode()))
    print(await tt.recv())

    await tt.close()

    # This also shows hos to same object can be reused.


if __name__ == '__main__':
    trio.run(main)