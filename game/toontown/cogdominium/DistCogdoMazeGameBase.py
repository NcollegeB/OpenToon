# This module provides shared dist Cogdo maze game behavior and data used by related implementations
# in Cogdo rooms, activities, entities, and rewards.

from direct.showbase.RandomNumGen import RandomNumGen
from toontown.cogdominium.CogdoMaze import CogdoMazeFactory
from . import CogdoMazeGameGlobals as Globals

class DistCogdoMazeGameBase:

    def createRandomNumGen(self):
        return RandomNumGen(self.doId)

    def createMazeFactory(self, randomNumGen):
        return CogdoMazeFactory(randomNumGen, Globals.NumQuadrants[0], Globals.NumQuadrants[1])
