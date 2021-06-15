# Routing

The most complex part of this project is the routing. Here I will explain various methods of routing, as well as their pros and cons.

## Everyone knows Everyone

The "Everyone Knows Everyone" system is the simplest type of routing we can implement. Everyone knows Everyone. When Client A wants to send data to Client Z, it already knows the address of Client Z. It can directly connect. Every time a new client connects, the entry node notifies every other client.

Pros:
- Simple to implement
- Relatively fast
Cons:
- Does not scale.

This solution does not scale well in reality, even though it looks like it would at first.

Imagine you have two networks, networks A and B. Each network is separated, except for one computer that is part of both networks. When we have PYDEVTS running on all nodes of each network, the only computer that can talk to both networks is the one in the middle, and each computer of each network *thinks* that it can access the other network. But when it tries, it fails.

## Hop Based

The second method of routing is hop-based. The computer that starts it creates a message that has the target node id and a hop counter. It then sends the message to every computer it knows, which then decrements the hop counter and checks if it is the recipient. If it is not the recipient and the hop counter is > 0, it sends the message to every node it knows. Propagation continues until the hop counter has reached zero, and then it stops.

Pros:
- Slightly Scalable
Cons:
- Not as easy to implement as the previous system
- Limits the size of the network (nothing further than x hops)
- Adds overhead and strain on unrelated parts of the network
- Message duplication

Hop-based systems are much more scalable than the previous system. This system is capable of reliably sending messages between networks in the afore-mentioned scenario. This system also has some overhead when sending messages, but not enough to be noticeable. This system is still simple enough to implement but may have slightly more complex code.

The largest downside is message duplication. Multiple versions of the same message *will* reach the target. This makes it no suitable for most applications.

## Pathfinding

The pathfinding system is my personal favorite and is also the hardest to implement. It is fast, scalable, and reduces overhead and computational draw on the entirety of the cluster. As opposed to hop-based, this system only broadcasts to all nodes on the first message, and all subsequent messages use the same path to send a message to the recipient. 

Similar to the "Everyone Knows Everyone" system, the Pathfinding approach has a list of peers. However, this list of peers contains only direct neighbors of the current node, not every node on the network. To rephrase, The Pathfinding node's list of peers consists of every peer that has *directly* accessed it by either forwarding or sending a request to it with zero jumps.

### The header

The pathfinding routing system uses a simple header on the first request: a string containing the node ID of the target and a hop counter. The body of the message is also simple: a list of 32-bit integers.

### Starting a request

When starting a request, the pathfinding routing system iterates over all of its direct peers. For each peer, it logs the index of the peer in this list.

```python
for i,peer in enumerate(peers):
    ...
```

Then it generates a packet for each peer, with the header containing a default hop count and the node ID of the target. The body consists of the index of the current peer. Then the node sends the packet to each peer.

```python
for i, peer in enumerate(peers):
    packet = generate_packet(to,i)
    peer.send_packet()
```

When the peer receives the packet, it adds the previous index to the list and repeats the process for its peers.

When the node that owns the node id receives the packet, it adds the previous node to the list and then uses the odd and even 32-bit integers in the message to generate two lists looking like so:

|  SEND  |  RECV  |
-------------------
|   01   |   33   |
|   11   |   12   |
|   22   |   27   |

RECV is the list of indexes to get to the node. SEND is the list of indexes to get back from the node.

The recipient node saves the list under the node id of its sender, and then it used this list to send a message containing these lists back to the sender node. 

If a pathfinding routing system finds multiple paths, they are sorted according to length and used as a redundancy if any hops fail.

If all routes fail, the entire process can be re-attempted, and if that fails, the system increases the hop count, and the connection is re-attempted. If this does not work, the system assumes that the node no longer exists.

### Broadcast Pathfinding

The pathfinding system can also map the entire network by sending a "broadcast" signal instead of a direct connection to a specific node ID. All nodes will then send back the info as if they were the recipient and then continue to forward the request. A scalable version of "Everyone Knows Everyone" can also be built with this.

Pros
- Scalable
- Can build a topology map of the network
- Cache routes
Cons
- IO intensive for the initial connection
- Makes building fast fire-and-forget applications hard
    - For example, HTTP would not work well on something like this, although database synchronization would work well.
- Network size limited by x number of hops

## Map Based

The map-based system is derived from Pathfinding (To be specific, Broadcast Pathfinding) and works on a network map. Every time a client connects to the network, it downloads a map from the entry node (which includes itself) and then uses a system similar to Hop Based and Pathfinding that broadcasts a message to the entire network, telling each node to add the new client to its map. The on>ly difference is that instead of using a hop count, the nodes check if the client is already in their map, and if it is, they do not propagate the message. Instead of using the Pathfinding broadcast method, it would use the map to find the shortest path. Then it would generate a packet similar to the Pathfinding method packet.

Pros
- Largely Scalable
- Caching routes can be done but is not required
- Network Size not limited
- Works across different networks