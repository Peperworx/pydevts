from ..routers import BasicRouter

class P2PConnection:
    """
        Represents a connection to a peer to peer cluster.
    """
    def __init__(self, entry):
        """
            Represents a connection to a peer to peer cluster.
        """
        # Validate entry
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise AttributeError("Entry must be a tuple of (str, int)")
        
        # Check entry[0] is a string
        if not isinstance(entry[0], str):
            raise AttributeError("Entry must be a tuple of (str, int)")
        
        # Check entry[1] is a number / string of number
        if isinstance(entry[1], str):
            if entry[1].isdecimal():
                self.entry = (entry[0], int(entry[1]))
            else:
                raise AttributeError("Entry must be a tuple of (str, int)")
        elif not isinstance(entry[1], int):
            raise AttributeError("Entry must be a tuple of (str, int)")
        else:
            self.entry = entry
        
        self.router = BasicRouter(self)

    async def __aenter__(self) -> "P2PConnection":

        # Prepare security
        await self.router.prepare_security()

        # Connect router to entry node
        await self.router.connect_to(self.entry[0], self.entry[1])

        # Return self
        return self
    
    async def __aexit__(self, *args) -> "P2PConnection":
        pass