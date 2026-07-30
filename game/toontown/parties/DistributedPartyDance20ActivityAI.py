# This module implements the authoritative AI-server side of party dance 20 activity, handling
# validated state and synchronized gameplay for party scheduling, activities, decorations, and
# services.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyDance20ActivityAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyDance20ActivityAI')
