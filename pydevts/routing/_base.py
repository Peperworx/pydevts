"""
    Provides a base class for routing.
"""

class _Router:
    """A Base class for pydevts routers
    """

    def __init__(self, keypair: tuple[str, str] = (None, None)):
        """Initialize the router

        Args:
            keypair (tuple[str, str], optional): The public-private keypair to use for encryption. Defaults to (None, None).
        """

        raise NotImplementedError()
    
    async def enter(self, host: str, port: int, tls: bool = False):
        """Enters a cluster

        Args:
            host (str): The entry host of the cluster
            port (int): The entry port of the cluster
            tls (bool, optional): Whether to use TLS. Defaults to False.
        """

        raise NotImplementedError()
    
    async def sendto(self, node_id: str, data: bytes):
        """Sends data to a node

        Args:
            node_id (str): The ID if the node to send to
            data (bytes): The data to send
        """

        raise NotImplementedError()
    
    async def on_connection(self, connection)