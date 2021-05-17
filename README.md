# PYDDS

PYDDS (Python Distributed Data Store) is a distributed data store and event system written in python and based on the concept of nodes.

PYDDS is beign developed for [schuaro](https://github.com/peperworx/schuaro) but is being developed as a separate project. It is intended for use as a cache and for messaging between backend services.

## Architecture

A PYDDS cluster consists of nodes.
- Each node knows about another node
- Each node only stores and updates data when needed
- Nodes discover their peers by a link to at least one other peer.


### Information format

PYDDS uses a database/key-value system. This means that keys and values are stored in a database. Each PYDDS cluster can have more than one database. Keys consist of any strings, and values consist varying types. (Dictionaries, lists, strings, integers)

### Information sharing

Nodes only learn about information as it is created, updated, read, or deleted. When a node connects to the network, it learns about all of the databases and keys, but does not know about the specific data. Data is only pulled from the cluster when it is requested from the node, or when the data is updated on another node. Non-stale data is also read from other nodes, but not at initialization time (Another thread takes care of this)

### Stale data

Stale data is data which has not been read or written to recently. Generally, each database has a set expiration time for the contents. When the expiration time has elapsed, (current_time - last_accessed_time >= expiration time) data is not replicated, but is still kept.

### Clients

Clients work differently in PYDDS. Clients connect to the network exactly like nodes do, and data is replicated to the clients in the same way. However, clients can not be used as gateways into the network. This makes clients extremely similar to nodes.

### Module systems

PYDDS is designed to be modular. This means that you can add nodes to the network that perform different tasks. For example: making sure that specific sets of data do not go stale, persisting data to disk, performing analytics, etc.


### Event systems

PYDDS is designed around the concept of event systems. When something happens, everyone knows. This is what allows for the afore mentioned Module System, and allows information sharing to work. Clients and Nodes can also register custom events to communicate amongst themselves. 

### Single node systems

A PYDDS Cluster can run with any number of nodes, including just a single node.