# This module declares the UberDOG-side distributed placeholder for the Toontown SpeedChat relay; it
# adds only a notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class TTSpeedchatRelayUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTSpeedchatRelayUD')
