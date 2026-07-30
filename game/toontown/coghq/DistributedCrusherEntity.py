# This module implements the client-side distributed crusher entity, handling network updates,
# presentation, and player interaction for Cog HQ facilities, bosses, rooms, and level entities.

from otp.level import BasicEntities
from direct.directnotify import DirectNotifyGlobal

class DistributedCrusherEntity(BasicEntities.DistributedNodePathEntity):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCrusherEntity')

    def __init__(self, cr):
        BasicEntities.DistributedNodePathEntity.__init__(self, cr)

    def announceGenerate(self):
        BasicEntities.DistributedNodePathEntity.announceGenerate(self)
        self.crushMsg = self.getUniqueName('crushMsg')
