# This module implements the UberDOG side of Toon, providing global or persistent services shared
# across districts.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedToonUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonUD')
