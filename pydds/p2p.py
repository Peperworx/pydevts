"""
    This file contains classes for creating P2P connections over TCP.
"""
import socket
import trio

import logging
import struct

logging.basicConfig(level=logging.DEBUG)

class P2PConnection:
    def __init__(self,target_address: str, target_port: int):
        """
            A basic peer to peer connection for sending raw data between two systems.
        """

        # Address and port of the initial peer.
        self.target_address = target_address
        self.target_port = target_port


        self.messages = {}

        self.peers = []

        self.system_events = {
            "server_join":self._server_joined,
            "peer_joined":self._peer_joined
        }
        
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
        try:
            init_peer = await trio.open_tcp_stream(self.target_address,self.target_port)
            logging.info(f"Connected to peer {self.target_address}:{self.target_port}")
        except socket.gaierror or OSError:
            logging.warning(f"Unable to connect to peer {self.target_address}:{self.target_port}. Still awaiting connections")
            init_peer = None
        
        
        # Create server object
        self.server = (await trio.open_tcp_listeners(0,host="0.0.0.0"))[0]
        
        # Log that we are listening
        logging.info(f"Created server at {self.server.socket.getsockname()[0]}:{self.server.socket.getsockname()[1]}")


        # If we have connected to peer
        if init_peer:
            # Request server information from them
            await self._send(
                init_peer, 1, "server_join",
                struct.pack("LL",
                    len(self.server.socket.getsockname()[0]),
                    self.server.socket.getsockname()[1]
                ) + self.server.socket.getsockname()[0].encode()
            )
            returns = struct.unpack("L",(await init_peer.receive_some(struct.calcsize("L"))))[0]
            data = b""
            if returns > 0:
                data = await init_peer.receive_some(returns)
            
            # Populate list of peers
            offset = 0
            while offset < len(data):
                header = struct.unpack("LL",data[offset:offset+struct.calcsize("LL")])
                offset += struct.calcsize("LL")
                # Grab port
                port = header[1]

                # Grab hostname
                host = data[offset:offset+header[0]].decode()
                offset += header[0]

                # Add to list of peers
                if (host, port,) not in self.peers:
                    self.peers.append((host,port,))
            
            # Add the initial client
            self.peers.append((self.target_address,self.target_port,))
        print(self.peers)
        # Serve the listeners
        await trio.serve_listeners(self._serve,[self.server])

    async def _send(self, stream: trio.SocketStream, msg_type: int, name: str, data: bytes):
        """
            Internal function to send message to client.
        """

        # Pack the header
        header = struct.pack("BLL",msg_type,len(name),len(data))

        # Pack the data
        send_data = header + name.encode() + data

        # Send the data
        await stream.send_all(send_data)

    async def _serve(self, server_stream):
        """
            Internal function for serving requests
        """
        
        logging.debug(f"Message from {server_stream.socket.getpeername()[0]}:{server_stream.socket.getpeername()[1]}")

        header = struct.unpack("BLL",await server_stream.receive_some(struct.calcsize("BLL")))
        
        # Recieve the message name and data
        if header[1] > 0:
            name = (await server_stream.receive_some(header[1])).decode()
        else:
            name = ""
        if header[2] > 0:
            data = await server_stream.receive_some(header[2])
        else:
            data = b""
        if header[0] == 0: # If it is a message type of zero
            # Log it
            logging.debug(f"Recieved event '{name}'")
        elif header[0] == 1: # If it is a system message
            # Log it
            logging.debug(f"Recieved system event '{name}'")

            # Try to call it
            if name in self.system_events.keys():
                await self.system_events[name](server_stream, server_stream.socket.getpeername()[0], server_stream.socket.getpeername()[1], data)

    async def _server_joined(self, ss, host, port, data):
        """
            Called when a peer requests to join
        """

        logging.info(f"Peer {host}:{port} joined network")
        
        
        
        
        
        # Generate data for other peers
        peerdata = bytearray()

        for peer in self.peers:
            peerdata += struct.pack("LL",len(peer[0]), peer[1]) + peer[0].encode()

        senddata = struct.pack("L",len(peerdata)) + bytes(peerdata)

        

        # Send peers list
        await ss.send_all(senddata)

        for peer in self.peers:
            conn = await trio.open_tcp_stream(peer[0],peer[1])
            await self._send(conn,1,"peer_joined",
                struct.pack("LL",
                    len(host),
                    port
                ) + host.encode()
            )
        
        # Add to peers
        self.peers.append((host,port,))
        
    async def _peer_joined(self, ss, host, port, data):
        """
            Called when a peer joins
        """
        print("Peer Joined")
        print(data)