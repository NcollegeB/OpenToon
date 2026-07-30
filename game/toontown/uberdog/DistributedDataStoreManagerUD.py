# This module declares the UberDOG-side distributed placeholder for data-store services; it adds
# only a notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedDataStoreManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDataStoreManagerUD')
