# This module implements the client-side distributed Donald's Dreamland treasure, handling network
# updates, presentation, and player interaction for playgrounds, treasures, and safe-zone
# activities.

from . import DistributedSZTreasure

class DistributedDLTreasure(DistributedSZTreasure.DistributedSZTreasure):

    def __init__(self, cr):
        DistributedSZTreasure.DistributedSZTreasure.__init__(self, cr)
        self.modelPath = 'phase_8/models/props/zzz_treasure'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
