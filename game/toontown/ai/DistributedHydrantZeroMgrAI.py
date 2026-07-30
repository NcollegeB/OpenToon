# This module declares the AI-side distributed placeholder for the hydrant-zero event manager; it
# adds only a notification category and no event behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedHydrantZeroMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedHydrantZeroMgrAI')
