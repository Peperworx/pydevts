"""Implements system for MultiPeer P2P connections
"""


class P2PConnection:
    """Peer to peer data passing
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 0):
        """Initialize P2PConnection

        Args:
            host (str): The hostname to host on
            port (int, optional): The port to host on. Defaults to 0.
        """
        self.host = host
        self.port = port
    
    