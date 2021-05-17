"""
    This file contains classes for creating P2P connections over TCP.
"""
import socket
import trio

class P2PConnection:
    def __init__(self,target_address: str, target_port: int):
        """
            A basic peer to peer connection for sending raw data between two systems.
        """
        self.target_address = target_address
        self.target_port = target_port
        self.messages = {}
        
    def listen(self, message):
        """
            Listen for a message
        """
        def deco(func):
            if message not in self.messages.keys():
                self.messages[message] = []
            self.messages[message] += [func]
            return func
        return deco

    def start(self):
        """
            Starts the asyncio server
        """
        trio.run(self._start)
    
    async def _start(self):
        """
            Internal start function
        """
        
        # Create a client object
        self.client = await trio.open_tcp_stream(self.target_address,self.target_port)

        

    async def _serve(self):
        """
            Internal function for serving requests
        """
        pass
    