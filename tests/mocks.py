from dataclasses import dataclass
from types import FunctionType
from typing import Optional
import uuid
import random

@dataclass
class Mock_P2PNode_1:
    """
        This is a class a lot of the tests will be using to
        check value modification.
    """
    callbacks: dict[str, list[FunctionType]]
    entry: dict

    nid: str = uuid.uuid4()
    listen_port: int = random.randint(0,65535)
    

class Mock_Connection_1:
    """
        This is a mock connection that simply pushes to stack and pops from stack
        while statically generating responses.
    """
    
    @classmethod
    def connect(cls, host, port):
        self.host = host
        self.port = port
        if host == "fail":
            raise OSError("Mock is supposed to fail")
        return cls()
    
    async def recv(self) -> dict:
        ...
    async def send(self, data: dict):
        ...


