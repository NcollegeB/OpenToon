# This module implements the authoritative AI-server side of party valentine jukebox 40 activity,
# handling validated state and synchronized gameplay for party scheduling, activities, decorations,
# and services.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyValentineJukebox40ActivityAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyValentineJukebox40ActivityAI')
