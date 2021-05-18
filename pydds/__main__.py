from .p2p import *

import sys

p2p = P2PConnection("localhost",int(sys.argv[1]))
p2p.start()