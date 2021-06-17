"""
    Implements basic protocol base classes.
"""
from types import CoroutineType, TracebackType
from typing import Optional, Type
from pydevts.protocol import AddressType



class PYDEVTSTransport:
    """
        Base class for all transport protocols
    """
    address: AddressType
    

    def __init__(self, address: AddressType):
        """
            Initiates transport object with address.
            The usage of this address will be determined by further methods called.
        """
        
        # Set address in self
        self.address = address

        
    
    
    
    async def serve(self, callback: CoroutineType):
        """
            This function creates a blocking server that binds to the address specified
            in the constructor of this class. Does not return and must be called asynchronously.
            When a connection is received, callback is executed.
        """
        ...


    async def open(self) -> "PYDEVTSTransport":
        """
            This function opens a client that connects to a server at the address
            specified in the constructor of this class.
            As a convenience, this method returns self.
        """

        return self
    
    async def close(self):
        """
            This function closes the current client, or stops the current server.
        """
        ...

    async def __aopen__(self) -> "PYDEVTSTransport":
        """
            Context manager __aopen__ that wraps self.open
        """

        return await self.open()
    
    async def __aclose__(self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tcbk: Optional[TracebackType]):
        """
            Context manager __aclose__ that wraps self.close
        """

        await self.close()


    
    async def send(self, data: bytes):
        """
            Sends a message consisting of {data}
        """

        ...
    
    async def recv(self, size: Optional[int] = 0) -> bytes:
        """
            Receives a message of max size {size}
            If {size} is not provided, it will default to an implementation 
            specific value.
        """

        return b""
