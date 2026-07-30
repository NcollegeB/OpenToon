# This module provides AI-server logic for catalog, coordinating authoritative simulation and state
# for catalog items, purchasing, delivery, and catalog interfaces.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class CatalogManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('CatalogManagerAI')

    def startCatalog(self):
        pass

    def deliverCatalogFor(self, _):
        pass
