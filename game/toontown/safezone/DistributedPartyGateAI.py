# This module implements the authoritative AI-server side of party gate, handling validated state
# and synchronized gameplay for playgrounds, treasures, and safe-zone activities.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyGateAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyGateAI')
