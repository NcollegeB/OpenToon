# This module provides shared Cogdo crane game behavior and data used by related implementations in
# Cogdo rooms, activities, entities, and rewards.

from toontown.cogdominium import CogdoCraneGameSpec
from toontown.cogdominium import CogdoCraneGameConsts as Consts

class CogdoCraneGameBase:

    def getConsts(self):
        return Consts

    def getSpec(self):
        return CogdoCraneGameSpec
