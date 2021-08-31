"""
    Messages with a number type. Commonly used for routing systems.
"""

# Serialization
import struct

class MsgNum:
    """
        Serialization class for messages with a numbered type.
    """

    _fmt = "!BQ" # type, length
    _size = struct.calcsize(_fmt)

    @staticmethod
    def dumps(message_type: int, data: bytes) -> bytes:
        """Serializes the message into bytes

        Args:
            message_type (int): The type of message being sent
            data (bytes): The data in that message

        Returns:
            bytes: The serialized data
        """

        return struct.pack(MsgNum._fmt, message_type, len(data)) + data

    @staticmethod
    def loads(data: bytes) -> tuple[int, bytes]:
        """Deserializes bytes into a tuple of message type and data

        Args:
            data (bytes): The input data

        Returns:
            tuple[int, bytes]: The tuple of message type and data
        """

        msg_type, msg_len = struct.unpack(MsgNum._fmt, data[:MsgNum._size])
        return msg_type, data[MsgNum._size:MsgNum._size + msg_len]

