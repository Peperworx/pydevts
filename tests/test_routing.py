import pytest
from . import mocks
from pydevts.routers.basic import EKERouter
from pydevts.p2p import P2PNode
from random import randint
import uuid

@pytest.mark.usefixtures("router")
@pytest.mark.usefixtures("anyio_backend")
class TestBasicRouter:

    @pytest.fixture(autouse=True)
    def _create_router(self, router):
        # Real quick mock a P2PNode
        self.p2p = mocks.Mock_P2PNode_1(
            callbacks={},
            entry={}
        )

        # Create some values
        self.p2p.nid = uuid.uuid4()
        self.p2p.listen_port = randint(1,65535)
        

        # Create the router instance
        self.router = router(self.p2p)
    async def test_init(self, router, mocker):
        """
            Tests initialization of router
        """
        

        # Verify NID
        assert self.router.owner.nid == self.p2p.nid

        # Verify listen port
        assert self.router.owner.listen_port == self.p2p.listen_port
    
    async def test_connect_to_fail(self, router, mocker):
        """
            This tests the router connecting to the network
        """

        # First mock the connection class
        mocker.patch("pydevts.conn.Connection",mocks.Mock_Connection_1)

        # Create the hosts and port
        conn_host = "fail"
        conn_port = 0000

        # Try to connect
        entry = await self.router.connect_to(conn_host, conn_port)

        # Assert failed
        assert entry == None

    async def test_connect(self, router, mocker):
        """
            This tests the router connecting to the network
        """

         # First mock the connection class
        mocker.patch("pydevts.conn.Connection",mocks.Mock_Connection_1)

        # Create the hosts and port
        conn_host = "success"
        conn_port = 0000

        # Try to connect
        entry = await self.router.connect_to(conn_host, conn_port)
        
        # Assert failed
        assert entry == None

