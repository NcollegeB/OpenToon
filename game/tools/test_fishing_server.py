"""Focused tests for the authoritative ordinary-fishing server path.

Run from the game directory with the bundled ``ppython`` interpreter.
"""

import math
import pathlib
import sys
import unittest
from unittest.mock import patch

from panda3d.core import ClockObject
from panda3d.core import NodePath
from panda3d.core import Point3


GAME_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from toontown.ai.FishManagerAI import FishManagerAI
from toontown.fishing import FishCollection
from toontown.fishing import FishGlobals
from toontown.fishing import FishTank
from toontown.safezone.DistributedFishingSpotAI import DistributedFishingSpotAI
from toontown.toonbase import ToontownGlobals


class _QuestManager:
    def __init__(self):
        self.item = None
        self.calls = []

    def findItemInWater(self, av, zoneId):
        self.calls.append((av.doId, zoneId))
        return self.item


class _Air:
    def __init__(self):
        self.questManager = _QuestManager()


class _Avatar:
    def __init__(self):
        self.doId = 1001
        self.fishCollection = FishCollection.FishCollection()
        self.fishTank = FishTank.FishTank()
        self.maxFishTank = 20
        self.fishingRod = 0
        self.fishingTrophies = []
        self.money = 0
        self.maxHp = 15
        self.hp = 15
        self.collectionUpdates = []
        self.tankUpdates = []

    def getMaxFishTank(self):
        return self.maxFishTank

    def getFishingRod(self):
        return self.fishingRod

    def getMoney(self):
        return self.money

    def takeMoney(self, amount, useBank=True):
        if self.money < amount:
            return False
        self.money -= amount
        return True

    def d_setFishCollection(self, *netLists):
        self.collectionUpdates.append(netLists)

    def b_setFishCollection(self, genusList, speciesList, weightList):
        self.fishCollection = FishCollection.FishCollection()
        self.fishCollection.makeFromNetLists(
            genusList, speciesList, weightList)
        self.d_setFishCollection(genusList, speciesList, weightList)

    def d_setFishTank(self, *netLists):
        self.tankUpdates.append(netLists)

    def addMoney(self, amount):
        self.money += amount

    def b_setFishTank(self, genusList, speciesList, weightList):
        self.fishTank = FishTank.FishTank()
        self.fishTank.makeFromNetLists(genusList, speciesList, weightList)
        self.d_setFishTank(genusList, speciesList, weightList)

    def getFishingTrophies(self):
        return self.fishingTrophies

    def b_setFishingTrophies(self, trophies):
        self.fishingTrophies = list(trophies)

    def getMaxHp(self):
        return self.maxHp

    def b_setMaxHp(self, maxHp):
        self.maxHp = maxHp

    def toonUp(self, amount):
        self.hp = min(self.maxHp, self.hp + amount)


class FishManagerTests(unittest.TestCase):
    def setUp(self):
        self.air = _Air()
        self.manager = FishManagerAI(self.air)
        self.avatar = _Avatar()

    def test_quest_item_precedes_normal_catch_and_updates_quest_manager(self):
        self.air.questManager.item = 42
        result = self.manager.generateCatch(
            self.avatar, ToontownGlobals.ToontownCentral)
        self.assertEqual(result, [FishGlobals.QuestItem, 42, 0, 0])
        self.assertEqual(
            self.air.questManager.calls,
            [(self.avatar.doId, ToontownGlobals.ToontownCentral)])
        self.assertEqual(len(self.avatar.fishTank), 0)

    def test_fish_catch_updates_collection_and_tank(self):
        self.manager._chooseItemType = lambda: FishGlobals.FishItem
        with patch.object(
                FishGlobals,
                'getRandomFishVitals',
                return_value=(1, 0, 0, 32)):
            result = self.manager.generateCatch(
                self.avatar, ToontownGlobals.ToontownCentral)

        self.assertEqual(result, [FishGlobals.FishItemNewEntry, 0, 0, 32])
        self.assertEqual(len(self.avatar.fishCollection), 1)
        self.assertEqual(len(self.avatar.fishTank), 1)
        self.assertEqual(len(self.avatar.collectionUpdates), 1)
        self.assertEqual(len(self.avatar.tankUpdates), 1)

    def test_failed_fish_vitals_become_boot_not_invalid_fish(self):
        self.manager._chooseItemType = lambda: FishGlobals.FishItem
        with patch.object(
                FishGlobals,
                'getRandomFishVitals',
                return_value=(0, 0, 0, 0)):
            result = self.manager.generateCatch(
                self.avatar, ToontownGlobals.ToontownCentral)

        self.assertEqual(result, [FishGlobals.BootItem, 0, 0, 0])
        self.assertEqual(len(self.avatar.fishCollection), 0)
        self.assertEqual(len(self.avatar.fishTank), 0)

    def test_jellybean_catch_uses_current_rod_reward(self):
        self.avatar.fishingRod = 2
        self.manager._chooseItemType = lambda: FishGlobals.JellybeanItem
        result = self.manager.generateCatch(
            self.avatar, ToontownGlobals.ToontownCentral)
        self.assertEqual(
            result,
            [FishGlobals.JellybeanItem, FishGlobals.Rod2JellybeanDict[2], 0, 0])
        self.assertEqual(self.avatar.money, FishGlobals.Rod2JellybeanDict[2])

    def test_full_tank_cannot_receive_quest_or_normal_reward(self):
        self.avatar.maxFishTank = 0
        self.air.questManager.item = 42
        result = self.manager.generateCatch(
            self.avatar, ToontownGlobals.ToontownCentral)
        self.assertEqual(result, [FishGlobals.OverTankLimit, 0, 0, 0])
        self.assertEqual(self.air.questManager.calls, [])

    def test_sale_clears_tank_and_awards_each_new_trophy_once(self):
        for species in range(20):
            genus = FishGlobals.getGenera()[species // 5]
            validSpecies = species % len(FishGlobals.getSpecies(genus))
            weight = FishGlobals.getRandomWeight(genus, validSpecies)
            self.avatar.fishCollection.collectFish(
                self._makeFish(genus, validSpecies, weight))
        self.avatar.fishTank.getTotalValue = lambda: 123

        result = self.manager.creditFishTank(self.avatar)

        self.assertTrue(result)
        self.assertEqual(self.avatar.money, 123)
        self.assertEqual(len(self.avatar.fishTank), 0)
        self.assertEqual(
            self.avatar.fishingTrophies,
            list(range(len(self.avatar.fishCollection) //
                       FishGlobals.FISH_PER_BONUS)))
        self.assertEqual(
            self.avatar.maxHp,
            15 + len(self.avatar.fishingTrophies))
        self.assertFalse(self.manager.creditFishTank(self.avatar))

    def test_spot_claims_are_unique_per_avatar(self):
        first = object()
        second = object()
        self.assertTrue(self.manager.claimSpot(self.avatar.doId, first))
        self.assertTrue(self.manager.claimSpot(self.avatar.doId, first))
        self.assertFalse(self.manager.claimSpot(self.avatar.doId, second))
        self.manager.releaseSpot(self.avatar.doId, second)
        self.assertIs(self.manager.getSpotForAvatar(self.avatar.doId), first)
        self.manager.releaseSpot(self.avatar.doId, first)
        self.assertIsNone(self.manager.getSpotForAvatar(self.avatar.doId))

    def test_requested_fish_must_be_catchable_by_current_rod(self):
        self.avatar.fishingRod = 0
        self.manager.requestedFish[self.avatar.doId] = (6, 0)
        self.assertIsNone(self.manager._getRequestedFish(self.avatar))
        self.assertNotIn(self.avatar.doId, self.manager.requestedFish)

    @staticmethod
    def _makeFish(genus, species, weight):
        from toontown.fishing.FishBase import FishBase
        return FishBase(genus, species, weight)


class _CastAir:
    def __init__(self, avatar, manager):
        self.avatar = avatar
        self.fishManager = manager
        self.doId2do = {avatar.doId: avatar}
        self.events = []

    def getAvatarIdFromSender(self):
        return self.avatar.doId

    def writeServerEvent(self, *event):
        self.events.append(event)


class _SpotHarness:
    doCast = DistributedFishingSpotAI.doCast
    _writeSuspicious = DistributedFishingSpotAI._writeSuspicious
    _getCastLanding = DistributedFishingSpotAI._getCastLanding
    _isTargetInRange = DistributedFishingSpotAI._isTargetInRange
    vZeroMax = DistributedFishingSpotAI.vZeroMax
    angleMax = DistributedFishingSpotAI.angleMax
    gravity = DistributedFishingSpotAI.gravity
    bobStartY = DistributedFishingSpotAI.bobStartY
    bobStartZ = DistributedFishingSpotAI.bobStartZ
    targetHitTolerance = DistributedFishingSpotAI.targetHitTolerance

    def __init__(self, air, avatar):
        self.air = air
        self.notify = type(
            '_Notify',
            (),
            {'warning': lambda unusedSelf, unusedMessage: None})()
        self.avId = avatar.doId
        self.cast = False
        self.castPower = 0.0
        self.castHeading = 0.0
        self.castStartTime = 0.0
        self.pondDoId = 2001
        self.posHpr = [-63.5335, 41.648, -3.36708, 120.0, 0.0, 0.0]
        self.movies = []
        self.cancelCalls = 0
        self.timeoutCalls = 0

    def d_setMovie(self, *args):
        self.movies.append(args)

    def _cancelMovieLater(self):
        self.cancelCalls += 1

    def _resetTimeout(self):
        self.timeoutCalls += 1


class FishingCastValidationTests(unittest.TestCase):
    def setUp(self):
        self.avatar = _Avatar()
        self.avatar.money = 20
        self.manager = FishManagerAI(_Air())
        self.air = _CastAir(self.avatar, self.manager)
        self.air.doId2do[2001] = type(
            '_Pond',
            (),
            {'getArea': lambda unusedSelf: ToontownGlobals.ToontownCentral})()
        self.spot = _SpotHarness(self.air, self.avatar)

    def test_valid_cast_is_charged_once_and_marks_pending(self):
        cost = FishGlobals.getCastCost(self.avatar.getFishingRod())
        self.spot.doCast(0.75, 15.0)
        self.assertTrue(self.spot.cast)
        self.assertEqual(self.avatar.money, 20 - cost)
        self.assertEqual(self.spot.movies[-1][0], FishGlobals.CastMovie)
        self.assertEqual(self.spot.cancelCalls, 1)
        self.assertEqual(self.spot.timeoutCalls, 1)

        self.spot.doCast(0.75, 15.0)
        self.assertEqual(self.avatar.money, 20 - cost)
        self.assertEqual(len(self.air.events), 1)

    def test_invalid_cast_parameters_are_rejected_without_charge(self):
        self.spot.doCast(1.5, 15.0)
        self.assertFalse(self.spot.cast)
        self.assertEqual(self.avatar.money, 20)
        self.assertEqual(self.spot.movies, [])
        self.assertEqual(len(self.air.events), 1)

    def test_target_hit_must_match_landing_position_and_cast_timing(self):
        self.spot.castPower = 0.75
        self.spot.castHeading = 0.0
        landing = self.spot._getCastLanding()
        self.assertIsNotNone(landing)

        root = NodePath('root')
        pier = root.attachNewNode('pier')
        pier.setPosHpr(*self.spot.posHpr)
        angleNode = pier.attachNewNode('angle')
        angleNode.setH(self.spot.castHeading)
        transformed = angleNode.getMat(root).xformPoint(
            Point3(0.0, self.spot.bobStartY +
                   self.spot.castPower * self.spot.vZeroMax *
                   math.cos(math.radians(
                       self.spot.castPower * self.spot.angleMax)) *
                   landing[3], 0.0))
        self.assertAlmostEqual(landing[0], transformed[0], places=4)
        self.assertAlmostEqual(landing[1], transformed[1], places=4)

        target = type(
            '_Target',
            (),
            {'getExpectedPosition': lambda unusedSelf: landing[:3]})()
        self.spot.castStartTime = (
            ClockObject.getGlobalClock().getRealTime() -
            landing[3] - 1.0)
        self.assertTrue(self.spot._isTargetInRange(target))

        distantTarget = type(
            '_Target',
            (),
            {'getExpectedPosition': lambda unusedSelf: (
                landing[0] + self.spot.targetHitTolerance + 1.0,
                landing[1],
                landing[2])})()
        self.assertFalse(self.spot._isTargetInRange(distantTarget))

        self.spot.castStartTime = ClockObject.getGlobalClock().getRealTime()
        self.assertFalse(self.spot._isTargetInRange(target))


if __name__ == '__main__':
    unittest.main(verbosity=2)
