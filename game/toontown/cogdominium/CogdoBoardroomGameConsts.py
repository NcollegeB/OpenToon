# This module defines shared constants, configuration values, and lookup tables for Cogdo boardroom
# game within Cogdo rooms, activities, entities, and rewards.

from direct.fsm.StatePush import StateVar
from otp.level.EntityStateVarSet import EntityStateVarSet
from toontown.cogdominium.CogdoEntityTypes import CogdoBoardroomGameSettings
Settings = EntityStateVarSet(CogdoBoardroomGameSettings)
GameDuration = StateVar(60.0)
FinishDuration = StateVar(10.0)
