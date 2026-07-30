# This module implements the client-side distributed minigame physics world, handling network
# updates, presentation, and player interaction for trolley minigame rules, presentation, and
# synchronization.

from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.minigame import MinigamePhysicsWorldBase

class DistributedMinigamePhysicsWorld(DistributedObject.DistributedObject, MinigamePhysicsWorldBase.MinigamePhysicsWorldBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMinigamePhysicsWorld')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        MinigamePhysicsWorldBase.MinigamePhysicsWorldBase.__init__(self, canRender=1)

    def delete(self):
        MinigamePhysicsWorldBase.MinigamePhysicsWorldBase.delete(self)
        DistributedObject.DistributedObject.delete(self)
