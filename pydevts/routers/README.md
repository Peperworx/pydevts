# Routing

The most complex part of this project is certaintly the routing. Here I will explain various methods of routing, as well as their pros and cons.

## Everyone knows Everyone

This is the most simple type of routing we can implement. Simply: Everyone knows Everyone. When Client A wants to send data to Client Z, it already knows the address of Client Z so it directly connects. Everytime a new Client connects, every existing client is notified by the entry node.

Pros:
- Simple to implement
- Relatively fast
Cons:
- Does not scale.

This solution may seem like it scales well at first glance, but in reality it does not.

Imagine you have two networks, network A and B. Each network is separated, except for one computer that is part of both networks. When we have PYDEVTS running on all nodes of each network, the only computer that can talk to both networks is the one in the middle, and each computer of each network *thinks* that it can access the other network, but when it tries, it fails.

## Hop Based

The second method of routing is hop based. The computer that starts it creates a message that has the target node id and a hop counter. It then sends the message to every computer it knows, which then decrements the hop counter and checks if it is the target of the message. If it is not the recepient and the hop counter is > 0, then it sends it to every node it knows. This continues until the hop counter has reached zero, and then it stops.

Pros:
- Scalable
Cons:
- Some overhead
- Not as easy to implement as the previous system

This is much more scalable than the previous system. In the same scenario as detailed before, this would be able to reliably send messages to nodes on both networks. This system also has some overhead when sending messages, but not enough to be noticible. This system is still simple enough to implement, but may have slightly more complex code.

## Pathfinding

This is my personal favorite, and is also the hardest to implement. It is fast, scalable, and reduces overhead and computational draw on the entirety of the cluster. As apposed to hop based, this system only broadcasts to all nodes on the first message, and all subsequent messages use the same path to send a message to the recepient. 

Similar to 'Everyone knows Everyone' the Pathfinding approach has a list of peers. However, this list of peers is only direct neighbors of the current node, not of every node on the network. To rephrase, The Pathfinding node's list of peers contains a list of every peer that has *directly* accessed it by either forwarding or sending a request to it with zero jumps.

### The header

The pathfinding routing system uses a simple header on the first request: a string containing the node ID of the target, and a hop counter. The body of the message is also simple: a list of 32 bit integers.

### Starting a request

To start a request a pathfinding routing system iterates over all of it's direct peers. For each peer, it logs the index of the peer in this list.

```python
for i,peer in enumerate(peers):
    ...
```

Then it generates a packet for each peer, with the header containing a default hop count and the node ID of the target. The body contains the index of the current peer being iterated over. Then the node sends the packet for each peer.

```python
for i, peer in enumerate(peers):
    packet = generate_packet(to,i)
    peer.send_packet()
```

The peer then accepts the packet, adds the index of the sender to the end of the packet, and then forwards the packet along the network in the same manner.

When the node that owns the node id recieves the packet, it adds the previous node to the list, and then uses the odd and even 32 bit integers in the packet to generate two lists looking like so:

|  SEND  |  RECV  |
-------------------
|   01   |   33   |
|   11   |   12   |
|   22   |   27   |

Where RECV is the list of indexes to get to the node, and SEND is the list of indexes to get back from the node.

This list is than saved on the recepient node under the node id of its sender, and then it used this list to send a message containing these lists back to the sender node.

After this is complete, this same list can be used to generate routes to and from the sender node.

If multiple routes are found, they are sorted according to length, and used if any hops are unable to be made, or routing fails (due to disconnected and reconnected node, network failures, etc.)

If all routes fail, the entire process can be re-attempted, and if that fails, hop count is increased and the connection is re-attempted. If this fails, it can be assumed that the node no-longer exists.

## Notify Pathfinding

The pathfinding system can also be used to map the entire network by sending a "broadcast" siginal instead of a direct connection to a specific node ID. This will cause all nodes to send back the info as if they were the recepient, and then continue to forward the request. This can be used for administration purposes, and also for a system similar to the 'Everyone knows Everyone' system, but scalable.