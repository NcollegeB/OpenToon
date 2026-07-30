# This module declares the AI-side distributed placeholder for trick-or-treat targets; it adds only
# a notification category and no event behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedTrickOrTreatTargetAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTrickOrTreatTargetAI')
