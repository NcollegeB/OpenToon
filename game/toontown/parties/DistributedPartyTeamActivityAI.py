# This module implements the authoritative AI-server side of party team activity, handling validated
# state and synchronized gameplay for party scheduling, activities, decorations, and services.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyTeamActivityAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyTeamActivityAI')
