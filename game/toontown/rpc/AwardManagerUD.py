# This module declares the UberDOG-side global award endpoint used by the distributed award service.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class AwardManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('AwardManagerUD')
