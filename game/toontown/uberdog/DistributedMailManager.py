# This module declares the persistent client-side distributed mail-manager object and currently adds
# no mail behavior beyond its base class.

from direct.distributed.DistributedObject import DistributedObject

class DistributedMailManager(DistributedObject):
    neverDisable = 1
