"""
    Serialization for messages with a named type.
"""

# Serialization
import struct
import msgpack


class MsgName:
    """
        Serialization class for messages with a named type.
    """

    _fmt = "!Q" # length
    _size = struct.calcsize(_fmt)

    @staticmethod
    def dumps(message_type: str, data: bytes) -> bytes:
        """Serializes the message into bytes

        Args:
            message_type (str): The type of message being sent
            data (bytes): The data in that message

        Returns:
            bytes: The serialized data
        """
        data = msgpack.packb((message_type, data))
        return struct.pack(MsgName._fmt, len(data)) + data

    @staticmethod
    def loads(data: bytes) -> tuple[int, bytes]:
        """Deserializes bytes into a tuple of message type and data

        Args:
            data (bytes): The input data

        Returns:
            tuple[int, bytes]: The tuple of message type and data
        """

        msg_len = struct.unpack(MsgName._fmt, data[:MsgName._size])[0]
        msg_type, msg_data = msgpack.unpackb(data[MsgName._size:MsgName._size + msg_len])
        return msg_type, msg_data
