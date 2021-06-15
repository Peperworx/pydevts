# PYDEVTS

PYDEVTS (Python Distributed EVenT System) is a distributed event system written in python and based on the concept of nodes that is designed for the implementation of data stores and other replicated systems.

PYDEVTS is based upon a simple concept: A cluster of nodes that can send and receive events.

PYDEVTS is also lightweight, requiring only [anyio](https://github.com/agronholm/anyio) although some examples may require additional libraries (these will be detailed in the examples description)


## How do I use this?

While more in-depth documentation will come in the future, currently there are several examples in the `examples/` folder.

Each example takes some command line arguments, which are detailed below. But first, we must define a few terms.




### Terms


#### Cluster Ports

A cluster port is a port with which a client will try to connect to a cluster. If the port is not reachable, the node starts as the first node in a cluster. A cluster port is any public port of a node in a cluster. Cluster ports are printed when a node starts and log level is INFO or DEBUG.

#### Host Ports

Sometimes PYDEVTS Nodes will run another application alongside themselves when running. If this application is a server of some kind, it's public facing port is called a Host Port.

### Examples

Listed below are some of the examples found in the `examples/` directory. All examples assume localhost.

#### fastapi_example.py

External Requirements:
- fastapi
- hypercorn

This example details how to run another async application (FastAPI with hypercorn) alongside PYDEVTS.

It takes two arguments:
- The cluster port to attempt to connect to
- The host port to host the fastapi application on

#### picklenode.py

External Requirements:
- trio (for the event loop)

NOTICE: This should never be used with untrusted data, as pickle can be used to execute untrusted code.

This example shows how to create a custom node type. This node stores a single pickled object, and can get and set the object in the cluster.

This example takes two arguments:
- The cluster port to attempt to connect to
- The literal string 'w' (without the quotes) if we want the cluster to update the value. If we do not provide this, the cluster will simply read the value every second and print it.

#### picklenodewriter.py

External Requirements:
- trio (for the event loop)

NOTICE: This should never be used with untrusted data, as pickle can be used to execute untrusted code.

This example works in conjunction with picklenode.py to show two different nodes types can work together. Every time the stored value in a picklenode.py node is updated, it writes the string representation of it to a file called `pickleoutput.txt`

This example takes one argument:
- The cluster port to attempt to connect to


## Versioning

This project is currently in its infancy. In all 0.y.z versions, there is no backward or forwards compatibility guaranteed. These versions each represent a stage in the development of the first full release: 1.0.0

What each 0.y.z version represents is listed here:

### 0.0.z

This version is the most unstable version. This version was to simply provide a ground for experimenting with methods, almost none of which persisted into the next version.

### 0.1.z

This version provides theoretical support for multiple routing systems, although it only provides a basic peer based routing system at 0.1.0, future patch versions will add more routing systems. For example: 0.1.1 will provide a basic hop-based routing system.

### 0.2.z

This is where things start to get interesting. From versions 0.0.z and 0.1.z we now know the basics about how the system will function when finished. In this version we will start creating standard API interfaces and protocols for routing systems to use. This version will also implement QUIC as well as TCP to reduce overhead produced when connecting to peers, and use other external libraries to provide more extensive support for different routing methods.

### 0.3.z

This version will restructure the project to make the Routing Systems, Protocols, and P2P connections as modular as possible, as well as removing dependencies between different classes to completely decouple systems and allow, for example, routing systems to be used with a different library, or allow someone to implement, say, STCP as the communication protocol used.

### 0.4.z

This version is an API refractor. This focuses mainly on how nodes work (combining nodes, removing unneeded methods, etc.), and will allow users to provide custom data serialization methods. The goal of this version is to make the library as ergonomic as possible, whilst adding customization that was not included in 0.3.z.

### 0.5.z

This version will focus on security and hardening the system against denial of service attacks and similar attacks. A patch version of this version will also provide support for plugins that allow certain aspects of the system to be changed (e.x: load balancing connections), or to perform operations (like analytics) on received or sent data. This plugin system works at the connection level, and not at the node level like custom nodes do.

### 0.6.z and up

These versions are yet to be determined, and will most likely be used in the event of an occurring issue or feature that I have not yet thought of, or do not fit into the other versions. These versions will be filled in here as needed.

### 1.y.z and up

These versions are the first stable versions and will follow the semver versioning system. These will mainly be bugfixes and new features.
## Collaboration and Questions

If you find a bug, report it on github issues. If, however, you have questions or are not sure how something works, post it on github discussions.

If you see some room for improvement and you wish to help out, create a github issue describing the problem and stating that you can work on it. If you do not wish to help out, or can not for some reason, then still leave the issue, as any feedback is appreciated. Usability and efficiency feedback is appreciated even more.

