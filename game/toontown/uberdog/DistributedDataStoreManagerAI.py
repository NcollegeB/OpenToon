# This module declares the AI-side distributed placeholder for data-store services; it adds only a
# notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedDataStoreManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDataStoreManagerAI')
