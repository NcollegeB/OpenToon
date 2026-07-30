# This module implements the authoritative AI-server side of changing statuary, handling validated
# state and synchronized gameplay for estates, houses, gardens, mailboxes, closets, and banks.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedChangingStatuaryAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedChangingStatuaryAI')
