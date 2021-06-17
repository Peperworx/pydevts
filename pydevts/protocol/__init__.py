from typing import Union

AddressType = Union[
    tuple[str,int], # Support standard sockets
    str,            # Support unix sockets
]