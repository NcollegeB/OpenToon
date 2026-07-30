# This module defines Cog population and encounter placement for Lawbot office boiler room trap 00
# Cogs in the Cog facility level system.

from .SpecImports import *
from toontown.toonbase import ToontownGlobals
CogParent = 100001
BattleCellId = 0
BattleCells = {BattleCellId: {'parentEntId': CogParent,
                'pos': Point3(0, 0, 0)}}
CogData = []
ReserveCogData = []
