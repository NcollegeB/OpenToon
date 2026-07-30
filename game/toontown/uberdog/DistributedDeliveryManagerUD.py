# This module declares the UberDOG-side distributed placeholder for delivery services; it adds only
# a notification category and no service behavior of its own.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedDeliveryManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDeliveryManagerUD')
