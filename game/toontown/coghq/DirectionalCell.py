# This module defines directional cell and its supporting behavior for Cog HQ facilities, bosses,
# rooms, and level entities.

from . import ActiveCell
from direct.directnotify import DirectNotifyGlobal

class DirectionalCell(ActiveCell.ActiveCell):
    notify = DirectNotifyGlobal.directNotify.newCategory('DirectionalCell')

    def __init__(self, cr):
        ActiveCell.ActiveCell.__init__(self, cr)
