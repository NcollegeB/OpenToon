"""Focused fishing data, persistence, and client-contract regression tests.

Run with the bundled game interpreter:
    ..\runtime\Panda3D-1.11.0-x64\python\ppython.exe \
        tools\test_fishing_persistence.py

These tests deliberately stop at the client/data boundary. Authoritative cast
validation, bean transactions, tank limits, quest credit, and selling belong
to the AI server and require separate integration tests.
"""

import pathlib
import re
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

GAME_ROOT = pathlib.Path(__file__).resolve().parents[1]
RESOURCE_ROOT = GAME_ROOT / 'resources'
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from panda3d.core import Point3
from panda3d.core import loadPrcFileData

loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'model-path %s' % RESOURCE_ROOT.as_posix())

from direct.showbase.ShowBase import ShowBase

game = ShowBase()
game.wantKarts = False
# FishGlobals.getValue() checks the client repository for fishing holidays.
game.cr = SimpleNamespace(newsManager=None)

from toontown.fishing import FishBase
from toontown.fishing import FishCollection
from toontown.fishing import FishGlobals
from toontown.fishing import FishTank
from toontown.fishing import DistributedFishingPond
from toontown.safezone import DistributedFishingSpot
from toontown.toon import DistributedToon


def _fish(genus, species, weight):
    return FishBase.FishBase(genus, species, weight)


class _MessengerSpy:
    def __init__(self):
        self.events = []

    def send(self, event, sentArgs=None, taskChain=None):
        self.events.append((event, sentArgs, taskChain))


class _BingoManagerSpy:
    def __init__(self):
        self.lastCatch = None

    def setLastCatch(self, catch):
        self.lastCatch = catch


class _PondForBingo:
    def __init__(self, manager):
        self.pondBingoMgr = manager

    def handleBingoCatch(self, catch):
        return DistributedFishingPond.DistributedFishingPond.handleBingoCatch(
            self, catch)


class _PondPresence:
    def __init__(self, present):
        self.present = present

    def hasPondBingoManager(self):
        return self.present


class FishTankTests(unittest.TestCase):
    def test_add_remove_and_invalid_indexes(self):
        tank = FishTank.FishTank()
        first = _fish(0, 0, 16)
        second = _fish(2, 0, 32)
        third = _fish(4, 0, 48)

        self.assertEqual(tank.addFish(first), 1)
        self.assertEqual(tank.addFish(second), 1)
        self.assertEqual(tank.addFish(third), 1)
        self.assertEqual(tank.removeFishAtIndex(1), 1)
        self.assertEqual(
            [fish.getVitals() for fish in tank.getFish()],
            [first.getVitals(), third.getVitals()],
        )

        self.assertEqual(tank.removeFishAtIndex(-1), 0)
        self.assertEqual(tank.removeFishAtIndex(len(tank)), 0)
        self.assertEqual(
            [fish.getVitals() for fish in tank.getFish()],
            [first.getVitals(), third.getVitals()],
        )

    def test_network_list_round_trip_uses_fresh_fish_objects(self):
        source = FishTank.FishTank()
        source.addFish(_fish(0, 0, 16))
        source.addFish(_fish(2, 1, 40))
        source.addFish(_fish(4, 2, 64))

        payload = source.getNetLists()
        restored = FishTank.FishTank()
        restored.makeFromNetLists(*payload)

        self.assertEqual(
            [fish.getVitals() for fish in restored.getFish()],
            [(0, 0, 16), (2, 1, 40), (4, 2, 64)],
        )
        self.assertIsNot(source.getFish()[0], restored.getFish()[0])
        self.assertEqual(restored.getNetLists(), payload)

    def test_total_value_and_capacity_behavior(self):
        tank = FishTank.FishTank()
        fish = [_fish(0, 0, 16), _fish(2, 0, 32)]
        for catch in fish:
            tank.addFish(catch)

        expectedValue = sum(catch.getValue() for catch in fish)
        self.assertEqual(tank.getTotalValue(), expectedValue)
        self.assertGreater(expectedValue, 0)

        avatar = SimpleNamespace(fishTank=tank, maxFishTank=2)
        self.assertTrue(
            DistributedToon.DistributedToon.isFishTankFull(avatar))
        avatar.maxFishTank = 3
        self.assertFalse(
            DistributedToon.DistributedToon.isFishTankFull(avatar))

        self.assertEqual(
            [FishGlobals.getCastCost(rod) for rod in range(5)],
            [1, 2, 3, 4, 5],
        )


class FishCollectionTests(unittest.TestCase):
    def test_new_entry_record_and_no_update(self):
        collection = FishCollection.FishCollection()

        self.assertEqual(
            collection.collectFish(_fish(0, 0, 16)),
            FishGlobals.COLLECT_NEW_ENTRY,
        )
        self.assertEqual(
            collection.collectFish(_fish(0, 0, 15)),
            FishGlobals.COLLECT_NO_UPDATE,
        )
        self.assertEqual(collection.getFish()[0].getWeight(), 16)
        self.assertEqual(
            collection.collectFish(_fish(0, 0, 24)),
            FishGlobals.COLLECT_NEW_RECORD,
        )
        self.assertEqual(collection.getFish()[0].getWeight(), 24)

        self.assertEqual(
            collection.getCollectResult(_fish(2, 0, 32)),
            FishGlobals.COLLECT_NEW_ENTRY,
        )
        self.assertEqual(len(collection), 1)

    def test_collection_network_round_trip_preserves_records(self):
        source = FishCollection.FishCollection()
        source.collectFish(_fish(0, 0, 24))
        source.collectFish(_fish(2, 0, 48))

        payload = source.getNetLists()
        restored = FishCollection.FishCollection()
        restored.makeFromNetLists(*payload)

        self.assertEqual(restored.getNetLists(), payload)
        self.assertTrue(restored.hasFish(0, 0))
        self.assertTrue(restored.hasGenus(2))
        self.assertEqual(len(restored), 2)


class AvatarReconnectTests(unittest.TestCase):
    def setUp(self):
        self.originalMessenger = getattr(DistributedToon, 'messenger', None)
        self.messenger = _MessengerSpy()
        DistributedToon.messenger = self.messenger

    def tearDown(self):
        if self.originalMessenger is None:
            del DistributedToon.messenger
        else:
            DistributedToon.messenger = self.originalMessenger

    @staticmethod
    def _avatar():
        return SimpleNamespace(uniqueName=lambda name: '%s-1234' % name)

    def test_all_fishing_avatar_fields_survive_reconnect_payload(self):
        collectionPayload = [[0, 2], [0, 1], [24, 48]]
        tankPayload = [[4, 0], [2, 0], [64, 16]]

        source = self._avatar()
        DistributedToon.DistributedToon.setFishCollection(
            source, *collectionPayload)
        DistributedToon.DistributedToon.setMaxFishTank(source, 30)
        DistributedToon.DistributedToon.setFishTank(source, *tankPayload)
        DistributedToon.DistributedToon.setFishingRod(source, 4)
        DistributedToon.DistributedToon.setFishingTrophies(
            source, [0, 2, 6])

        reconnect = self._avatar()
        DistributedToon.DistributedToon.setFishCollection(
            reconnect, *source.fishCollection.getNetLists())
        DistributedToon.DistributedToon.setMaxFishTank(
            reconnect, source.maxFishTank)
        DistributedToon.DistributedToon.setFishTank(
            reconnect, *source.fishTank.getNetLists())
        DistributedToon.DistributedToon.setFishingRod(
            reconnect, source.fishingRod)
        DistributedToon.DistributedToon.setFishingTrophies(
            reconnect, list(source.fishingTrophies))

        self.assertEqual(
            reconnect.fishCollection.getNetLists(), collectionPayload)
        self.assertEqual(reconnect.fishTank.getNetLists(), tankPayload)
        self.assertEqual(reconnect.maxFishTank, 30)
        self.assertEqual(reconnect.fishingRod, 4)
        self.assertEqual(reconnect.fishingTrophies, [0, 2, 6])
        self.assertEqual(
            [event[0] for event in self.messenger.events],
            ['fishTankChange-1234', 'fishTankChange-1234'],
        )


class FishingClientDefectTests(unittest.TestCase):
    def test_target_hit_detection_ignores_pond_depth_offset(self):
        hits = []
        scheduled = []
        target = SimpleNamespace(
            getDoId=lambda: 7001,
            getPos=lambda unusedRender: Point3(1.0, 1.0, -4.8),
            getRadius=lambda: 2.5,
        )
        pond = SimpleNamespace(
            notify=SimpleNamespace(
                debug=lambda unusedMessage: None,
                warning=lambda unusedMessage: None,
            ),
            localToonSpot=object(),
            localToonBobPos=Point3(0.0, 0.0, -1.4),
            targets={target.getDoId(): target},
            d_hitTarget=lambda caughtTarget: hits.append(caughtTarget),
            taskName=lambda name: name,
            checkTargets=lambda task=None: None,
        )
        scheduler = SimpleNamespace(
            doMethodLater=lambda *args: scheduled.append(args),
        )

        with patch.object(
                DistributedFishingPond, 'taskMgr', scheduler, create=True):
            DistributedFishingPond.DistributedFishingPond.checkTargets(pond)

        self.assertEqual(hits, [target])
        self.assertEqual(scheduled, [])

    def test_boot_item_label_marks_bingo_wildcard(self):
        spot = SimpleNamespace(
            pond=_PondPresence(True),
            itemLabel={},
        )
        labelMethod = (
            DistributedFishingSpot.DistributedFishingSpot
            ._DistributedFishingSpot__setItemLabel
        )

        labelMethod(spot, 'An old boot')
        self.assertEqual(
            spot.itemLabel['text'], 'An old boot\n\nBINGO WILDCARD')

        spot.pond = _PondPresence(False)
        labelMethod(spot, 'An old boot')
        self.assertEqual(spot.itemLabel['text'], 'An old boot')

    def test_bingo_boot_uses_the_existing_last_catch_path(self):
        manager = _BingoManagerSpy()
        pond = _PondForBingo(manager)

        DistributedFishingPond.DistributedFishingPond.handleBingoBoot(pond)

        self.assertEqual(manager.lastCatch, FishGlobals.BingoBoot)


class FishingDcContractTests(unittest.TestCase):
    def test_persistent_fishing_fields_keep_their_wire_contract(self):
        dcSource = (GAME_ROOT / 'etc' / 'toon.dc').read_text(
            encoding='utf-8')
        declarations = (
            r'setFishCollection\(uint8\[\] = \[\], uint8\[\] = \[\], '
            r'uint16\[\] = \[\]\) required ownrecv db;',
            r'setMaxFishTank\(uint8 = 20\) required ownrecv db;',
            r'setFishTank\(uint8\[\] = \[\], uint8\[\] = \[\], '
            r'uint16\[\] = \[\]\) required ownrecv db;',
            r'setFishingRod\(uint8 = 0\) required broadcast ownrecv db;',
            r'setFishingTrophies\(uint8\[\] = \[\]\) required ownrecv db;',
        )

        for declaration in declarations:
            self.assertIsNotNone(re.search(declaration, dcSource))


def tearDownModule():
    game.destroy()


if __name__ == '__main__':
    unittest.main(verbosity=2)
