"""
    Tests the PYDEVTS Message Protocol
"""
from pydevts.conn import PYDEVTSMessageProto
from anyio import create_task_group, run
import sys

async def on_msg(msg):
    print(msg)

app = PYDEVTSMessageProto(on_msg)

async def send_msg():
    if sys.argv[1] == "send":
        await app.send_to(sys.argv[2], sys.argv[3])

async def main():
    async with create_task_group() as tg:
        tg.start_soon(send_msg)
        await app.run()

run(main)