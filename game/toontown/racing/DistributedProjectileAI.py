# This module implements the authoritative AI-server side of projectile, handling validated state
# and synchronized gameplay for kart races, tracks, pads, projectiles, scores, and leaderboards.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedProjectileAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedProjectileAI')
