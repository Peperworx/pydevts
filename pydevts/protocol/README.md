# PYDEVTS Communication protocol

The PYDEVTS communication protocol is build on UDP and designed similar to TCP, with some added features.

## Connection Types

The PYDEVTS protocol has two connection types. Stream and message.

### Stream

The stream protocol type is most similar to TCP. You send and receive data in a connection, and then disconnect when you are done sending data.
This is implemented on top of the message system, which already provides most of what the stream system does provide.
### Message

The message protocol is the hybrid of UDP and TCP. The server sends a datagram, and if it does not receive an acknowledgement within a specified timeout, it sends it again. This is designed with the idea of delivering messages quickly without losing data. The message protocol is not ordered, meaning packets may not arrive in the order they were sent, and is designed for use in event systems, as well as other pseudo "fire-and-forget" systems.

## Security

The protocol is secured using an initial exchange including two messages, sent in plaintext, using the message connection type. The first message contains the following information:

- Contacting node's public key used for encryption
- Contacting node's public key used for signing
- Random 64 bit number generated by contacting node.

Once this message is received, the contacted node generates 32 bytes of data, and xor's the recieved random number with it (Looping the recieved number over and over again)

It then sends the second message as a response to the first:

- Contacted node's public key used for encryption
- Contacted node's public key used for signing
- The previously generated 32 bytes (not xored, and encrypted with the contacting node's public key for encryption)


The contacting node then decrypts the 32 bytes and xors them. (This is used to ensure that a random number generator on one of the systems can not be rigged)

Those 32 bytes are then used to seed a random number generator, which is only used for the task of encryption for those two specific nodes, and each further message or datagram to the other node is sent AES encrypted with a number pulled from that number generator.

## Caching

Each node will keep a cache of other nodes that it has contacted. This includes their IP address, the port used, the initial random value used when connecting, the number of calls to the random number generator, and the last generated random number as the seed.

## Message format

When a message is sent, it contains a very basic header:


- The first and last 32 bits of the 32 byte number used when the node was first contacted. These combine to a 64 bit number which can be used to retrieve data about the other client from past requests. This is 0 if this is a first request, and if it is, no encryption attempts will be made, and no sensitive data will be transmitted.
- The length of the message body in bytes (32 bit integer)
- CRC32 code of data


That is it.
A few numbers.
And the Body.

If the body length is zero, and the CRC is non-zero, then it is an acknowledgement and the CRC is double checked to make sure we are talking about the same message. If we are not, find the message and verify it was sent. If that message was not sent, then the message should be ignored. A cache of all CRCs should be kept to minimize impact of improper responses, in case of DOS attacks.
