# This module declares the AI-side distributed placeholder for winter-caroling targets; it adds only
# a notification category and no event behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedWinterCarolingTargetAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedWinterCarolingTargetAI')
