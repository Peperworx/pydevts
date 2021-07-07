"""
    PYDEVTS P2P Protocol server and client implementations using TCP.
"""
import contextlib
import msgpack
import struct
import anyio


class PYDEVTSServer:

    def __init__(self, host, port):
        """
            Server implementing the PYDEVTS protocol
        """
        self.host = host
        self.port = port
        self.listener = None
        self.es = None
    
    async def __aenter__(self):
        """
            Asynchronous Context Manager Entry Point
        """

        # Create exit stack
        self.es = contextlib.AsyncExitStack()

        

    async def __aexit__(self, exc_type, exc, tb):
        """
            Asynchronous Context Manager Exit Point
        """

        # Close exit stack
        await self.es.aclose()

        # Clear exit stack
        self.es = None