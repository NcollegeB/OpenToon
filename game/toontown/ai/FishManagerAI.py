# This module provides AI-server logic for fish, coordinating authoritative simulation and state for
# district startup, holidays, events, and shared AI managers.

import random

from direct.directnotify import DirectNotifyGlobal

from toontown.fishing import FishGlobals
from toontown.fishing.FishBase import FishBase
from toontown.toonbase import ToontownGlobals


class FishManagerAI:
    """Authoritative fishing rewards, persistence, and pier ownership."""

    notify = DirectNotifyGlobal.directNotify.newCategory('FishManagerAI')

    def __init__(self, air, randomSource=None):
        self.air = air
        self.random = randomSource or random
        self.requestedFish = {}
        self._spotsByAvatar = {}

    def claimSpot(self, avId, spot):
        currentSpot = self._spotsByAvatar.get(avId)
        if currentSpot and currentSpot is not spot:
            return False
        self._spotsByAvatar[avId] = spot
        return True

    def releaseSpot(self, avId, spot):
        if self._spotsByAvatar.get(avId) is spot:
            del self._spotsByAvatar[avId]

    def getSpotForAvatar(self, avId):
        return self._spotsByAvatar.get(avId)

    def _getQuestItem(self, av, zoneId):
        questManager = getattr(self.air, 'questManager', None)
        if not questManager:
            return None
        return questManager.findItemInWater(av, zoneId)

    def _chooseItemType(self):
        roll = self.random.random() * 100.0
        for cutoff in FishGlobals.SortedProbabilityCutoffs:
            if roll <= cutoff:
                return FishGlobals.ProbabilityDict[cutoff]
        return FishGlobals.BootItem

    def _getRequestedFish(self, av):
        request = self.requestedFish.pop(av.doId, None)
        if request is None:
            return None

        genus, species = request
        try:
            speciesList = FishGlobals.getSpecies(genus)
        except (KeyError, TypeError):
            self.notify.warning('Discarding invalid requested fish genus %s for avatar %s.' %
                                (genus, av.doId))
            return None

        if not isinstance(species, int) or species < 0 or species >= len(speciesList):
            self.notify.warning('Discarding invalid requested fish species %s:%s for avatar %s.' %
                                (genus, species, av.doId))
            return None
        if not FishGlobals.canBeCaughtByRod(
                genus, species, av.getFishingRod()):
            self.notify.warning(
                'Discarding requested fish %s:%s that rod %s cannot catch for avatar %s.' %
                (genus, species, av.getFishingRod(), av.doId))
            return None
        return genus, species

    def _storeFish(self, av, genus, species, weight):
        fish = FishBase(genus, species, weight)
        if not av.fishTank.addFish(fish):
            self.notify.warning('Avatar %s fish tank rejected a validated catch.' % av.doId)
            return [FishGlobals.OverTankLimit, 0, 0, 0]

        collectResult = av.fishCollection.collectFish(fish)
        if collectResult == FishGlobals.COLLECT_NEW_ENTRY:
            itemType = FishGlobals.FishItemNewEntry
        elif collectResult == FishGlobals.COLLECT_NEW_RECORD:
            itemType = FishGlobals.FishItemNewRecord
        else:
            itemType = FishGlobals.FishItem

        collectionNetLists = av.fishCollection.getNetLists()
        av.b_setFishCollection(*collectionNetLists)

        tankNetLists = av.fishTank.getNetLists()
        av.b_setFishTank(*tankNetLists)
        return [itemType, genus, species, weight]

    def generateCatch(self, av, zoneId):
        """Roll and persist one catch after a pond validates the target hit."""

        if len(av.fishTank) >= av.getMaxFishTank():
            return [FishGlobals.OverTankLimit, 0, 0, 0]

        questItem = self._getQuestItem(av, zoneId)
        if questItem is not None:
            return [FishGlobals.QuestItem, questItem, 0, 0]

        requestedFish = self._getRequestedFish(av)
        if requestedFish is not None:
            genus, species = requestedFish
            weight = FishGlobals.getRandomWeight(genus, species, av.getFishingRod(), self.random)
            return self._storeFish(av, genus, species, weight)

        itemType = self._chooseItemType()
        if itemType == FishGlobals.FishItem:
            success, genus, species, weight = FishGlobals.getRandomFishVitals(
                zoneId, av.getFishingRod(), self.random)
            if not success:
                # Some pond/rod/rarity combinations have no entry. A boot is a
                # valid catch and avoids persisting the invalid 0:0 fish.
                return [FishGlobals.BootItem, 0, 0, 0]
            return self._storeFish(av, genus, species, weight)

        if itemType == FishGlobals.JellybeanItem:
            amount = FishGlobals.Rod2JellybeanDict[av.getFishingRod()]
            av.addMoney(amount)
            return [itemType, amount, 0, 0]

        return [FishGlobals.BootItem, 0, 0, 0]

    def creditFishTank(self, av):
        """Sell the tank, clear it, and grant newly earned fishing trophies."""

        saleValue = av.fishTank.getTotalValue()
        if saleValue:
            av.addMoney(saleValue)
        av.b_setFishTank([], [], [])

        totalFish = len(av.fishCollection)
        trophyCount = min(
            totalFish // FishGlobals.FISH_PER_BONUS,
            len(FishGlobals.TrophyDict))
        currentTrophies = list(av.getFishingTrophies())
        earnedTrophies = list(range(trophyCount))
        newTrophyCount = len([trophy for trophy in earnedTrophies
                              if trophy not in currentTrophies])
        if not newTrophyCount:
            return False

        newMaxHp = min(
            ToontownGlobals.MaxHpLimit,
            av.getMaxHp() + newTrophyCount)
        av.b_setMaxHp(newMaxHp)
        av.toonUp(newMaxHp)
        av.b_setFishingTrophies(earnedTrophies)
        return True
