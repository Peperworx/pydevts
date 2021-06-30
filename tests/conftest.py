import pytest
import os, sys

sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))


import pydevts

pytestmark = pytest.mark.anyio


@pytest.fixture(params=[
    pytest.param(('asyncio', {'use_uvloop': True}), id='asyncio+uvloop'),
    pytest.param(('asyncio', {'use_uvloop': False}), id='asyncio'),
    pytest.param(('trio', {'restrict_keyboard_interrupt_to_checkpoints': True}), id='trio')
])
def anyio_backend(request):
    return request.param