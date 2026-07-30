# This module implements the client-side distributed mint suit, handling network updates,
# presentation, and player interaction for Cog and boss actors, behavior, and combat support.

from toontown.suit import DistributedFactorySuit
from direct.directnotify import DirectNotifyGlobal

class DistributedMintSuit(DistributedFactorySuit.DistributedFactorySuit):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMintSuit')
