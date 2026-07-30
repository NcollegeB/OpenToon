# This module implements the client-side distributed Cogdo elevator int, handling network updates,
# presentation, and player interaction for Cogdo rooms, activities, entities, and rewards.

from toontown.building.DistributedElevatorInt import DistributedElevatorInt

class DistributedCogdoElevatorInt(DistributedElevatorInt):

    def _getDoorsClosedInfo(self):
        return ('cogdoInterior', 'cogdoInterior')
