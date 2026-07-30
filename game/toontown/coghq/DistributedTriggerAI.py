# This module implements the authoritative AI-server side of trigger, handling validated state and
# synchronized gameplay for Cog HQ facilities, bosses, rooms, and level entities.

from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from . import DistributedSwitchAI

class DistributedTriggerAI(DistributedSwitchAI.DistributedSwitchAI):
    pass
