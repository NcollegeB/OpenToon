# This module implements the client-side distributed e treasure, handling network updates,
# presentation, and player interaction for playgrounds, treasures, and safe-zone activities.

from . import DistributedSZTreasure

class DistributedETreasure(DistributedSZTreasure.DistributedSZTreasure):

    def __init__(self, cr):
        DistributedSZTreasure.DistributedSZTreasure.__init__(self, cr)
        self.modelPath = 'phase_4/models/props/icecream'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
