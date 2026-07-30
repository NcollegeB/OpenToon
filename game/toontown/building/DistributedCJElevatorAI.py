# This module implements the authoritative AI-server side of CJ elevator, handling validated state
# and synchronized gameplay for buildings, interiors, doors, elevators, and boarding.

from .ElevatorConstants import *
from . import DistributedBossElevatorAI

class DistributedCJElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=0)
        self.type = ELEVATOR_CJ
        self.countdownTime = ElevatorData[self.type]['countdown']
