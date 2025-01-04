"""
    Implements a multiple client cache
"""

# Connection class typehints
from ..proto._base import _Client
from ..proto import TCPClient

# Standard Library Imports
import time
import uuid

# Errors
from ..err import ConnectionNotFound

class MultiClientCache:

    _max_size: int
    _ttl: int
    _proto: _Client
    _cache: dict[str, list[_Client, int, tuple[str, int]]]

    def __init__(self, proto: _Client = TCPClient, max_size=100, ttl=60):
        """Initializes the cache

        Args:
            max_size (int, optional): The maximum size of the cache. Defaults to 100.
            ttl (int, optional): The time to live for a connection. Defaults to 60.
        """

        # Save the protocol
        self._proto = proto

        # Set the maximum size
        self._max_size = max_size

        # Set the ttl
        self._ttl = ttl

        # Create the cache
        self._cache = dict()

    async def connect(self, host: str, port: int) -> str:
        """Connects to a host.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.

        Returns:
            str: The connection ID. (handle)
        """

        # Create the connection ID
        connection_id = str(uuid.uuid4())

        # While the connection id is in the cache, create a new one
        while connection_id in self._cache.keys():
            # The odds of this happening are so low I might as well
            # just remove this code. Either way, one in a google is still
            # more than 0% chance of happening.
            connection_id = str(uuid.uuid4())

        # If the host and port are already in the cache
        for key, (_, created_at, addr) in self._cache.items():
            if addr[0] == host and addr[1] == port:
                # Reset the timer
                self._cache[key][1] = time.time()

                # Return the connection ID
                return key
        
        # Create the connection
        connection = await self._proto[0].connect(host, port)

        # Add the connection to the cache
        self._cache[connection_id] = [connection, time.time(), (host, port)]

        # Return the connection ID
        return connection_id

    async def send(self, handle: str, data: bytes):
        """Sends data to a connection.

        Args:
            handle (str): The connection ID.
            data (bytes): The data to send.
        """

        # If the connection is in the cache
        if handle in self._cache.keys():
            # Send the data
            await self._cache[handle][0].send(data)
        else:
            # Otherwise, raise an error
            raise ConnectionNotFound(f"Unable to find cached connection with ID {handle}")

    async def recv(self, handle: str) -> bytes:
        """Receives data from a connection.

        Args:
            handle (str): The connection ID.

        Returns:
            bytes: The data received.
        """

        # If the connection is in the cache
        if handle in self._cache.keys():
            # Receive the data
            return await self._cache[handle][0].recv()
        else:
            # Otherwise, raise an error
            raise ConnectionNotFound(f"Unable to find cached connection with ID {handle}")

    async def disconnect(self, handle: str):
        """Closes a connection.

        Args:
            handle (str): The connection ID.
        """

        # If the connection is in the cache
        if handle in self._cache.keys():
            # Close the connection
            await self._cache[handle][0].close()
            del self._cache[handle]
    
    async def close(self):
        """Closes all connections
        """

        # Loop through all connections
        for key in self._cache.copy().keys():
            # Close the connection
            await self._cache[key][0].close()
            del self._cache[key]
        

    def clean(self):
        """Cleans the cache of all expired connections.
        """

        # Loop through all connections
        for key, (_, created_at, _) in self._cache.items():
            
            # If the time is larger than 60, remove the connection
            if time.time() - created_at > 60:
                del self._cache[key]
    
    def remove_oldest(self):
        """Removes the oldest connection from the cache.
        """

        # Find the oldest connection
        oldest_key = None
        oldest_created_at = None
        for key, (_, created_at, _) in self._cache.items():
            if oldest_created_at is None or created_at < oldest_created_at:
                oldest_key = key
                oldest_created_at = created_at

        # Delete the oldest connection
        if oldest_key is not None:
            del self._cache[oldest_key]