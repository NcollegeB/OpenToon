# This module implements the authoritative AI-server side of franken donald, handling validated
# state and synchronized gameplay for classic-character NPC actors, paths, and dialogue.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedFrankenDonaldAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFrankenDonaldAI')
