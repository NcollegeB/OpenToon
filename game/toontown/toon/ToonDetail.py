# This module defines Toon detail and its supporting behavior for player Toon avatars, NPCs,
# inventory, and presentation.

from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.avatar import AvatarDetail
from toontown.toon import DistributedToon

class ToonDetail(AvatarDetail.AvatarDetail):
    notify = directNotify.newCategory('ToonDetail')

    def getDClass(self):
        return 'DistributedToon'

    def createHolder(self):
        toon = DistributedToon.DistributedToon(base.cr, bFake=True)
        toon.forceAllowDelayDelete()
        return toon
