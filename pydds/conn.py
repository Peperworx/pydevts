"""
    This file contains connection wrapper classes
"""
import trio


class Connection:
    def __init__(self, conn: trio.SocketStream):
        self.conn = conn
    
    async def recv(self) -> dict:
        """
        
        """