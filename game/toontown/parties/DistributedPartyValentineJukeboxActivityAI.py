# This module implements the authoritative AI-server side of party valentine jukebox activity,
# handling validated state and synchronized gameplay for party scheduling, activities, decorations,
# and services.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyValentineJukeboxActivityAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyValentineJukeboxActivityAI')
