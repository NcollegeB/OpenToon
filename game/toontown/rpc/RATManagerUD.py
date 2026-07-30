# This module declares the UberDOG-side global distributed endpoint for the RAT service.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class RATManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('RATManagerUD')
