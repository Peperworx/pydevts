# PYDDS

PYDDS (Python Distributed Data Store) is a distributed data store and event system written in python and based on the concept of nodes.

PYDDS is beign developed for [schuaro](https://github.com/peperworx/schuaro) but is being developed as a separate project. It is intended for use as a cache and for messaging between backend services.

## How to use it


Currently PYDDS simply implements a messaging system. An example of basic use of this library with FastAPI can be found in `example.py`

This file sets up a FastAPI endpoint at `/` and when the endpoint is called, sends a message to a member of the cluster (which uses our node ID, so it connects back to us). That event is then called, and echos data back to us. We then pass the data from that event into a broadcast event which is run on all members of the cluster.


