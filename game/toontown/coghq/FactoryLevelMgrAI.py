# This module provides AI-server logic for factory level, coordinating authoritative simulation and
# state for Cog HQ facilities, bosses, rooms, and level entities.

from otp.level import LevelMgrAI

class FactoryLevelMgrAI(LevelMgrAI.LevelMgrAI):

    def __init__(self, level, entId):
        LevelMgrAI.LevelMgrAI.__init__(self, level, entId)
        self.callSettersAndDelete('cogLevel')

    def setCogLevel(self, cogLevel):
        self.level.cogLevel = cogLevel
