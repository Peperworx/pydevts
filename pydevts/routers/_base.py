from typing import Optional


class RouterBase:

    

    def __init__(self, owner, **router_config):
        self.owner = owner
        self.config = router_config
    
    
    
    async def connect_to(self, host: str, port: int):
        """
            Executed when node is attempting to connect to cluster
            Arguments
            - {host}
                Host of the entry node
            - {port}
                Port of the entry node
        """
        pass
    
    async def send(self, target: str, data: bytes):
        """
            Executed when node wants to send raw data
            Arguments
            - {target}
                The NodeID of the target
            - {data}
                The raw data in bytes
        """
        pass

    async def receive(self, data: bytes) -> Optional[bytes]:
        """
            Executed when raw data is received
            Arguments
            - {data}
                The raw data in bytes
        """
        pass
    
    

