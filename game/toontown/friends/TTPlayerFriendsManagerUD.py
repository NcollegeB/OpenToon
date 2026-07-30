# This module provides UberDOG service logic for Toontown player friends, handling global or
# persistent coordination outside an individual district.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD

class TTPlayerFriendsManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTPlayerFriendsManagerUD')
