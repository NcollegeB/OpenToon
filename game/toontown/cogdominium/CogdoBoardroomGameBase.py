# This module provides shared Cogdo boardroom game behavior and data used by related implementations
# in Cogdo rooms, activities, entities, and rewards.

from toontown.cogdominium import CogdoBoardroomGameSpec
from toontown.cogdominium import CogdoBoardroomGameConsts as Consts

class CogdoBoardroomGameBase:

    def getConsts(self):
        return Consts

    def getSpec(self):
        return CogdoBoardroomGameSpec
