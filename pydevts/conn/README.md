# PYDEVTS Message Protocol

The PYDEVTS Message Protocol is a basic "connectionless" messaging protocol implemented UDP.
This protocol is very simple, and is designed to ensure that messages are delivered.

Messages are simple UDP packets with a short header containing the crc32 of the data.

The message exchange looks like the following:

If the arrow points to the right, it is sent by the contacting. If it points to the left, it is sent by the contacted.


Packet  ->  
        <-  ACK
Close   ->


If no ack is received within 3 seconds, the packet is re-sent. Maximum of 10 attempts.
Once the close packet is sent, the contacted is expected to stop sending immediately. Once ACK is sent, if close is not recieved within 3 seconds then ACK is resent. Maximum of 10 attempts.

Each client is required to keep a table of all currently "open" messages. That is, messages waiting on an ACK.
Each client is also required to keep a table of all incoming messages. Incoming messages are those that are still waiting on a close.

Each message has the following structure:

| NAME      | Size    |
| type      | 8  bits |
| success   | 8  bits |
| message ID| 16 bits |
| crc32     | 32 bits |

Then, there are a few rules to be followed:

1. When a node recieves a "Packet" type (type 0)
    - If the packet is already in the "open" list, and success is 0, skip the next step and resend the ACK.
    - The node should check the CRC32 of the contents of the message (Not including header)
        - If the crc32 fails, send an ACK (type 1) packet with success set to 1 (CRC32 failed)
        - If successful, send an ACK packet with success set to 0 (Success)
2. When a node recieves an "Ack" type (type 1)
    - If the ACK has a success of 1
        - The node should resend the packet, with a success of 1 (CRC32 failed)
    - The node should compare message IDs.
        - If the message ID is not in the "open" list, resend a close request using the information in the ACK
        - If the message ID is in the open list, remove it and then send the close request.
3. When a node recieves a "Close" type (type 3)
    - The node should remove the message from the incoming list.
    - Stop sending ACKs


There are also a few special cases

1. If a node sends a "Packet" and does not receive an "ACK" in three seconds
    - The node should resend the packet (maximum of 10 times)
2. If a node sends a "ACK" and does not recieve a "Close" in three seconds
    - The node should resend the "ACK" (maximum of 10 times)

