"""
    This file contains classes for creating P2P connections over TCP.
"""

import trio

import logging
import struct
import json
import uuid
from .conn import *



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
        conn = await trio.open_tcp_stream(host,int(port))
        

        # Request status
        await self._send(conn,{
            "type":"status"
        })

        # Recieve status
        status = await self._recv(conn)

        # Make sure that we got a status ping back
        if status['type'] != 'status':
            raise UnableToConnect()

        logging.debug(f"Server {host}:{port} has responded to status check.")
        

        # TODO: Credentials Here
        await self._send(conn, {
            "type":"register",
            "as":"node",
            "host_port": self.server.socket.getsockname()[1]
        })

        # Receive details
        data = await self._recv(conn)
        if data["type"] == "prepare_accept":
            logging.debug(f"We have been accepted")
            self.nid = data["id"]
        


        

    async def broadcast(self, name: str, data: dict):
        """
            Broadcast event {name} with data {data} to all peers.
        """
        rmp = []
        for peer in self.peers:
            try:
                conn = await Connection.connect(peer["host"], peer["port"])
                await conn.send({
                    "type":"message",
                    "from":self.nid,
                    "port":self.server.socket.getsockname()[1],
                    "name":name,
                    "data":data,
                })
                await conn.aclose()
            except OSError:
                rmp += [peer]
        [self.peers.remove(p) for p in rmp]

    async def sendto(self, peerid: str, name: str, data: dict):
        """
            Send event to peer with ID {peer}
        """
        
        for peer in self.peers:
            
            if peer["id"] == peerid:
                
                conn = await Connection.connect(peer["host"], peer["port"])
                await conn.send({
                    "type":"message",
                    "from":self.nid,
                    "port":self.server.socket.getsockname()[1],
                    "name":name,
                    "data":data,
                })
                await conn.aclose()
    
    async def start(self):
        """
            Starts the server
        """

        
        # Create a server
        self.server = (await trio.open_tcp_listeners(host="0.0.0.0",port=0))[0]

        # Attempt to initialize client
        try:
            # If we are the only instance, we generate out own node id
            self.nid = str(uuid.uuid4())
            await self._client_init()
        except OSError or UnableToConnect:
            
            logging.info(f"Unable to connect to remote {self.target_address}:{self.target_port}")

        host = self.server.socket.getsockname()[0]
        port = self.server.socket.getsockname()[1]

        logging.info(f"Hosting TCP server at address {host}:{port}")
        
        async with trio.open_nursery() as nursery:
            nursery.start_soon(trio.serve_listeners,self._serve, [self.server])
            nursery.start_soon(self._finish_startup)

    async def _finish_startup(self):
        """
            Finish startup
        """
        await trio.sleep(0.2)


        [await m() for m in self.messages["on_startup"]]

    async def _send(self, conn: trio.SocketStream, data: dict):
        """
            Sends data over a socket stream
        """

        # Pack the data
        packed = await self._pack(data)

        # Send the data
        await conn.send_all(packed)

    async def _emit(self, conn: trio.SocketStream, event: str, data: dict):
        """
            Emits an event over given stream
        """
        await self._send(conn, {
            "type":"message",
            "from":self.nid,
            "port":self.server.socket.getsockname()[1],
            "name":event,
            "data":data
        })

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
    
    async def _unpack(self, data: bytes) -> dict:
        """
            Unpacks data
        """
        offset = struct.calcsize("L")
        size = struct.unpack("L",data[:offset])[0]
        data = data[offset:offset+size].decode()
        return json.loads(data)

    async def _recv(self, ss) -> dict:
        """
            Receives data from a connection.
        """
        offset = struct.calcsize("L")
        recsize = await ss.receive_some(offset)
        if len(recsize) < offset:
            return {}
        size = struct.unpack("L",recsize)[0]
        data = (await ss.receive_some(size)).decode()
        data = json.loads(data)
        return data

    async def _serve(self, ss: trio.SocketStream):
        """
            Internal function for serving requests.
            This function handles a single request over the stream {ss}
        """


        
        async for data in ss:
            data = await self._unpack(data)
            # Log connection
            host = ss.socket.getpeername()[0]
            port = ss.socket.getpeername()[1]
            logging.debug(f"Message from {host}:{port}")
            

            if data["type"] == "status":
                await self._send(ss,{
                    "type":"status"
                })
            elif data["type"] == "register":
                logging.debug(f"Client {host}:{data['host_port']} is requesting to join cluster")
                await self._server_joined(ss, host, port, data)
            elif data["type"] == "new_node":
                logging.debug(f"Client {host}:{data['port']} is joining the cluster")
                await self._peer_joined(ss, host, port, data)
            elif data["type"] == "message":
                logging.debug(f"Client {host}:{data['port']} has sent message {data['name']}")
                if data["name"] in self.messages:
                    [await m(Connection(ss),data["data"]) for m in self.messages[data["name"]]]
            elif data["type"] == "peer_ready":
                self.peers.append({
                    "id":data["id"],
                    "host":host,
                    "port":data["port"],
                    "client_port":port
                })
            
    async def _server_joined(self, ss, host, port, data):
        """
            Called when a peer requests to join
        """

        # TODO: Credentials here

        # Generate a Node ID
        pid = str(uuid.uuid4())
        
        # Create peer request
        peer_request = {
            "type":"new_node",
            "id":pid,
            "host":host,
            "port":data["host_port"],
            "client_port":port
        }

        # Tell client to prepare for acceptance
        await self._send(ss,{
            "type":"prepare_accept",
            "id":pid,
            "host":host,
            "port":data["host_port"],
            "client_port":port
        })

        shost = self.server.socket.getsockname()[0]
        sport = self.server.socket.getsockname()[1]
        conn = await trio.open_tcp_stream(
            host = host,
            port = data["host_port"]
        )
        await self._send(conn, {
            "type":"peer_ready",
            "id":self.nid,
            "host":shost,
            "port":sport
        })
        await conn.aclose()

        # Re verify peer list
        await self._verify_peers()

        # Send to each peer
        for peer in self.peers:
            conn = await trio.open_tcp_stream(
                host=peer["host"],
                port=peer["port"]
            )
            await self._send(conn,peer_request)
            await conn.aclose()
        
        # Add to peers
        self.peers += [{
            "id":pid,
            "host":host,
            "port":data["host_port"],
            "client_port":port
        }]

        
    async def _peer_joined(self, ss, host, port, data):
        """
            Called when a peer joins
        """
        
        print("Peer Joined Network on external node")

        self.peers.append({
            "id":data["id"],
            "host":data["host"],
            "port":data["port"],
            "client_port":data["client_port"]
        })

        host = self.server.socket.getsockname()[0]
        port = self.server.socket.getsockname()[1]

        conn = await trio.open_tcp_stream(
            host = data["host"],
            port = data["port"]
        )
        await self._send(conn, {
            "type":"peer_ready",
            "id":self.nid,
            "host": host,
            "port": port
        })
        await conn.aclose()
    

    async def _verify_peers(self):
        """
            Verifies each peer, checking it it exists, removing it if it does not
        """
        
        rmp = []
        for peer in self.peers:
            try:
                conn = await trio.open_tcp_stream(
                    host=peer["host"],
                    port=peer["port"]
                )
                await self._send(conn, {
                    "type":"status"
                })
                recv = await self._recv(conn)
                if recv["type"] != "status":
                    rmp += [peer]
            except OSError:
                rmp += [peer]
        
        [self.peers.remove(p) for p in rmp if p in self.peers]

