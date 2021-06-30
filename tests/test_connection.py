import pytest
from pydevts.p2p.connection import P2PConnection
import os


@pytest.mark.usefixtures("anyio_backend")
class TestP2PConnection:
    """
        Tests a P2P connection
    """

    async def test_init_sets_value(self, anyio_backend):
        """
            Test if __init__ correctly sets the value
        """

        # Default value to test
        val = ("localhost",2233)

        # Create the connection object
        c = P2PConnection(entry=val)

        # Assert value set
        assert c.entry == val
    
    async def test_init_validates(self, anyio_backend):
        """
            Test if __init__ correctly validates the value
        """

        # These should fail
        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry=None)
        
        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry="1abcdef1")

        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry=("localhost", 2233, 4455))


        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry=(4124,2233))

        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry=(4124, "1abc1def1"))

        with pytest.raises(AttributeError) as exc_info:
            P2PConnection(entry=("localhost", "1abc1def1"))
        
    async def test_init_converts(self, anyio_backend):
        """
            Test if __init__ correctly converts values
        """

        # Conversion of strings as ports
        c = P2PConnection(entry=("localhost","2233"))
        assert c.entry[1] == 2233

    async def test_context(self, anyio_backend):
        """
            Tests that the context manager is behaving as expected
        """

        entry = ("localhost", 2233)
        async with P2PConnection(entry = entry) as c:
            # Verify entry real quick
            assert c.entry == entry 

    