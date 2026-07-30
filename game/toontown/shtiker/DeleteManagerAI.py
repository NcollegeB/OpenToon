# This module declares the AI-side distributed endpoint used by the Shticker Book inventory-deletion
# flow.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DeleteManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DeleteManagerAI')
