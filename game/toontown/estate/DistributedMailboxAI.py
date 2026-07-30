# This module implements the authoritative AI-server side of mailbox, handling validated state and
# synchronized gameplay for estates, houses, gardens, mailboxes, closets, and banks.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedMailboxAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMailboxAI')
