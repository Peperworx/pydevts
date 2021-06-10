# PYDEVTS

PYDEVTS (Python Distributed EVenT System) is a distributed event system written in python and based on the concept of nodes that is designed for the implementation of data stores and other replicated systems.

PYDEVTS is based upon a simple concept: A cluster of nodes that can send and recieve events.

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

## Collaboration and Questions

If you find a bug, report it on github issues. If, however, you have questions or are not sure how something works, post it on github discussions.

If you see some room for improvement and you wish to help out, create a github issue describing the problem and stating that you can work on it. If you do not wish to help out, or can not for some reason, then still leave the issue, as any feedback is appreciated. Usability and efficiency feedback is appreciated even more.