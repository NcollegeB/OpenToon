# This module declares the AI-side distributed placeholder for the Polar Place effect manager; it
# adds only a notification category and no event behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPolarPlaceEffectMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPolarPlaceEffectMgrAI')
