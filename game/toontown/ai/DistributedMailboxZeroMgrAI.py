# This module declares the AI-side distributed placeholder for the mailbox-zero event manager; it
# adds only a notification category and no event behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedMailboxZeroMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMailboxZeroMgrAI')
