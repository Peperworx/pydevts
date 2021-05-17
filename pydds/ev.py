"""
    This file contains the code for the distributed event system, which is the core for PYDDS
"""


# Sockets
import socket


# structures
from .structs import *
import struct



class EventNode:
    """
        A Node in an event system.
    """

    def send_event(self, evt_type: EEventType, name: str, data: bytes, s: socket.Socket):
        """
            Sends an event with name name and type evt_type with data data
        """

        # Construct the event structure
        estruct = EventDispatch(
            type=evt_type, name=name,
            data=data
        )

        # Pack the data

        epacked = struct.pack(
            "BLL",
            estruct.type,
            len(estruct.name),
            len(estruct.data)
        ) + bytes(estruct.name.encode()) + bytes(estruct.data)

        tsent = 0
        while tsent < len(epacked):
            sent = s.send(epacked[tsent:])
            if sent = 0:
                raise RuntimeError("Socket connection broken.")
            tsent+=sent
        