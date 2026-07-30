# This module implements the authoritative AI-server side of button, handling validated state and
# synchronized gameplay for Cog HQ facilities, bosses, rooms, and level entities.

from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from . import DistributedSwitchBase, DistributedSwitchAI

class DistributedButtonAI(DistributedSwitchAI.DistributedSwitchAI):
    setColor = DistributedSwitchBase.stubFunction
    setModel = DistributedSwitchBase.stubFunction
