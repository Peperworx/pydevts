"""
    This file contains classes for creating P2P connections over TCP.
"""
import socket
import trio

import logging
import struct
import sys
import json

logging.basicConfig(level=logging.DEBUG)

class UnableToConnect(Exception):
    pass

class P2PConnection:
    def __init__(self,target_address: str, target_port: int):
        """
            A basic peer to peer connection for sending raw data between two systems.
        """

        # Address and port of the initial peer.
        self.target_address = target_address
        self.target_port = target_port


        self.messages = {
            "on_startup":[]
        }

        self.peers = []

        self.system_events = {
            "server_join":self._server_joined,
            "peer_joined":self._peer_joined
        }

        self.ready = False

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

    async def _client_init(self):
        """
            Initializes the client.
        """

        # Grab the host and port
        host = self.target_address
        port = self.target_port

        # Create the connection
        conn = await trio.open_tcp_stream(
            host=host,
            port=int(port)
        )

        # Request status
        await self._send(conn, {
            "type":"status"
        })

        # Recieve status
        status = await self._recv(conn)

        # Make sure that we got a status ping back
        if status['type'] != 'status':
            raise UnableToConnect()
        
        
    
    async def start(self):
        """
            Starts the server
        """

        # Attempt to initialize client
        try:
            await self._client_init()
        except OSError or UnableToConnect:
            logging.info(f"Unable to connect to remote {self.target_address}:{self.target_port}")
        
        self.server = (await trio.open_tcp_listeners(host="0.0.0.0",port=0))[0]

        host = self.server.socket.getsockname()[0]
        port = self.server.socket.getsockname()[1]

        logging.info(f"Hosting TCP server at address {host}:{port}")
        
        await trio.serve_listeners(self._serve, [self.server])

    
    async def _send(self, conn: trio.SocketStream, data: dict):
        """
            Sends data over a socket stream
        """

        # Pack the data
        packed = await self._pack(data)

        # Send the data
        await conn.send_all(packed)

    async def _pack(self, data: dict) -> bytes:
        """
            Packs a JSON dictionary into a message for sending over TCP
        """

        # Dump the json
        data = json.dumps(data, separators=(',',':')).encode()

        # Grab the length
        data_len = len(data)

        # Pack and return data
        return struct.pack("L",data_len)+data
    
    async def _recv(self, ss) -> dict:
        """
            Receives data from a connection.
        """
        offset = struct.calcsize("L")
        size = struct.unpack("L",await ss.receive_some(offset))[0]
        data = (await ss.receive_some(size)).decode()
        data = json.loads(data)
        return data

    async def _serve(self, ss):
        """
            Internal function for serving requests.
            This function handles a single request over the stream {ss}
        """


        
        logging.debug(f"Message from {ss.socket.getpeername()[0]}:{ss.socket.getpeername()[1]}")

        # Unpack the data
        data = await self._recv(ss)

        if data["type"] == "status":
            await self._send(ss,{
                "type":"status"
            })

    async def _server_joined(self, ss, host, port, data):
        """
            Called when a peer requests to join
        """

        print("Peer joining network on this node")
        
    async def _peer_joined(self, ss, host, port, data):
        """
            Called when a peer joins
        """
        
        print("Peer Joined Network on external node")