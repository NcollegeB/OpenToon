# This module declares the client-side global distributed placeholder for data-store services and
# currently implements no data-store operations.

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from toontown.uberdog import DataStoreGlobals

class DistributedDataStoreManager(DistributedObjectGlobal):

    def __init__(self):
        pass
