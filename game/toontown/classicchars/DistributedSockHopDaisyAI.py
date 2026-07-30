# This module implements the authoritative AI-server side of sock hop daisy, handling validated
# state and synchronized gameplay for classic-character NPC actors, paths, and dialogue.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedSockHopDaisyAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSockHopDaisyAI')
