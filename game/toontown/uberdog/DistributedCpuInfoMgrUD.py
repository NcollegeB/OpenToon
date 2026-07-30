# This module declares the UberDOG-side distributed placeholder for CPU-information services; it
# adds only a notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedCpuInfoMgrUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCpuInfoMgrUD')
