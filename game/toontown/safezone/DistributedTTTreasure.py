# This module implements the client-side distributed Toontown treasure, handling network updates,
# presentation, and player interaction for playgrounds, treasures, and safe-zone activities.

from . import DistributedSZTreasure

class DistributedTTTreasure(DistributedSZTreasure.DistributedSZTreasure):

    def __init__(self, cr):
        DistributedSZTreasure.DistributedSZTreasure.__init__(self, cr)
        self.modelPath = 'phase_4/models/props/icecream'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
