# This module implements the authoritative AI-server side of Cogdo elevator ext, handling validated
# state and synchronized gameplay for Cogdo rooms, activities, entities, and rewards.

from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedElevatorExtAI import DistributedElevatorExtAI

class DistributedCogdoElevatorExtAI(DistributedElevatorExtAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogdoElevatorExtAI')

    def _createInterior(self):
        self.bldg.createCogdoInterior()
