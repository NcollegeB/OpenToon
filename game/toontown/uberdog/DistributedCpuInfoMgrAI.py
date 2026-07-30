# This module declares the AI-side distributed placeholder for CPU-information services; it adds
# only a notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedCpuInfoMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCpuInfoMgrAI')
