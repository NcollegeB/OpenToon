# This module provides UberDOG service logic for Toontown code redemption, handling global or
# persistent coordination outside an individual district.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class TTCodeRedemptionMgrUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTCodeRedemptionMgrUD')
