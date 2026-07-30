# This module implements the client-side distributed house item, handling network updates,
# presentation, and player interaction for estates, houses, gardens, mailboxes, closets, and banks.

from toontown.toonbase.ToontownGlobals import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
from direct.distributed import DistributedObject
from toontown.toonbase import TTLocalizer

class DistributedHouseItem(DistributedObject.DistributedObject):
    notify = directNotify.newCategory('DistributedHouseItem')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)

    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.load()

    def load(self):
        pass

    def disable(self):
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        DistributedObject.DistributedObject.delete(self)
