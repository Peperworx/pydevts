# PYDEVTS

PYDEVTS (Python Distributed EVenT System) is an event system designed for decentralized applications.

There are only two things that PYDEVTS provides: A Peer-To-Peer connection for sending data to a specific peer or broadcasting to all peers, and an event system built on top of this.

PYDEVTS can be seen as a serverless Socket.io.

This branch (the `dev` branch) is in development, and as such most things are not implemented. For a functional, yet not-so-stable version, check out (in both senses of the phrase) the branch `release-0.1.0` for something even less stable, yet more scalable (due to a hop-based router included) you can check out `0.1.1`

PYDEVTS should not be used in production, and doing so is at the risk of the user.

## Examples

Note: Most of these examples will not function, or even run at all. These serve as a reference for developers.


```python
from pydevts import Node
import sys

app = Node(entry_address="localhost", entry_port=int(sys.argv[1]))

@app.on("some_event")
async def some_event(sent_from: str, data: dict):
    print(f"Received event some_event from {sent_from} with data {data}")

# Automatically selects port, attempts to discover and use trio. If trio is not found, falls back to asyncio.
app.run()
```

Pydevts has three core functions that a user can use: `app.on`, `app.emit`, and `app.send`.

```python
# app.on registers an event handler
@app.on("some_event")
async def some_event(sent_from: str, data: dict):
    print(f"Received event some_event from {sent_from} with data {data}")

# app.send sends an event to a single node
app.send(node_id, event_name, event_data)

# app.emit sends an event to every node
app.emit(event_name, event_data)
```
