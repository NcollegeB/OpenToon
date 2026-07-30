# This module coordinates the client tutorial handshake and lifecycle, including entry, completion
# updates, skip requests, and the context-sensitive skip button.

from panda3d.core import *
from direct.gui.DirectGui import DirectButton, DGG
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals

class TutorialManager(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TutorialManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.skipTutorialButton = None
        self.skipTutorialPending = False

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        messenger.send('tmGenerate')
        self.accept('requestTutorial', self.d_requestTutorial)
        self.accept('requestSkipTutorial', self.d_requestSkipTutorial)
        self.accept('rejectTutorial', self.d_rejectTutorial)

    def disable(self):
        self.__cleanupSkipTutorialButton()
        self.ignoreAll()
        ZoneUtil.overrideOff()
        DistributedObject.DistributedObject.disable(self)

    def d_requestTutorial(self):
        self.sendUpdate('requestTutorial', [])

    def d_rejectTutorial(self):
        self.sendUpdate('rejectTutorial', [])

    def d_requestSkipTutorial(self):
        self.sendUpdate('requestSkipTutorial', [])

    def skipTutorialResponse(self, allOk):
        messenger.send('skipTutorialAnswered', [allOk])

    def enterTutorial(self, branchZone, streetZone, shopZone, hqZone):
        base.localAvatar.cantLeaveGame = 1
        ZoneUtil.overrideOn(branch=branchZone, exteriorList=[streetZone], interiorList=[shopZone, hqZone])
        messenger.send('startTutorial', [shopZone])
        self.acceptOnce('stopTutorial', self.__handleStopTutorial)
        self.acceptOnce('toonArrivedTutorial', self.d_toonArrived)
        self.__createSkipTutorialButton()

    def __handleStopTutorial(self):
        self.__cleanupSkipTutorialButton()
        base.localAvatar.cantLeaveGame = 0
        self.d_allDone()
        ZoneUtil.overrideOff()

    def __createSkipTutorialButton(self):
        self.__cleanupSkipTutorialButton()
        self.skipTutorialPending = False
        self.skipTutorialButton = DirectButton(
            parent=base.a2dBottomRight,
            relief=DGG.RAISED,
            frameColor=(0.2, 0.24, 0.3, 0.95),
            frameSize=(-3.5, 3.5, -0.75, 1.05),
            borderWidth=(0.08, 0.08),
            text='Skip Tutorial',
            text_fg=(1, 1, 1, 1),
            text_scale=0.7,
            text_pos=(0, 0.03),
            pos=(-0.31, 0, 0.14),
            scale=0.075,
            sortOrder=100,
            command=self.__requestActiveTutorialSkip)
        taskMgr.doMethodLater(
            0.25,
            self.__updateSkipTutorialButton,
            self.uniqueName('update-skip-tutorial-button'))

    def __cleanupSkipTutorialButton(self):
        taskMgr.remove(self.uniqueName('update-skip-tutorial-button'))
        taskMgr.remove(self.uniqueName('finish-skip-tutorial'))
        self.ignore('skipTutorialAnswered')
        if self.skipTutorialButton:
            self.skipTutorialButton.destroy()
            self.skipTutorialButton = None
        self.skipTutorialPending = False

    def __tutorialPlaceIsSafeToLeave(self):
        try:
            place = base.cr.playGame.getPlace()
            state = place.fsm.getCurrentState()
            return state and state.getName() == 'walk'
        except:
            return False

    def __updateSkipTutorialButton(self, task):
        if not self.skipTutorialButton:
            return task.done
        if self.skipTutorialPending or not self.__tutorialPlaceIsSafeToLeave():
            self.skipTutorialButton['state'] = DGG.DISABLED
        else:
            self.skipTutorialButton['state'] = DGG.NORMAL
        task.delayTime = 0.25
        return task.again

    def __requestActiveTutorialSkip(self):
        if self.skipTutorialPending or not self.__tutorialPlaceIsSafeToLeave():
            return
        self.skipTutorialPending = True
        self.skipTutorialButton['state'] = DGG.DISABLED
        self.acceptOnce(
            'skipTutorialAnswered',
            self.__handleActiveTutorialSkipResponse)
        self.d_requestSkipTutorial()

    def __handleActiveTutorialSkipResponse(self, allOk):
        if not allOk:
            self.skipTutorialPending = False
            return
        taskMgr.doMethodLater(
            0,
            self.__finishActiveTutorialSkip,
            self.uniqueName('finish-skip-tutorial'))

    def __finishActiveTutorialSkip(self, task):
        if not self.__tutorialPlaceIsSafeToLeave():
            task.delayTime = 0.25
            return task.again
        place = base.cr.playGame.getPlace()
        requestStatus = {
            'loader': 'safeZoneLoader',
            'where': 'playground',
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.ToontownCentral,
            'zoneId': ToontownGlobals.ToontownCentral,
            'shardId': None,
            'avId': -1}
        # The server has already authorized the skip and updated the tutorial
        # quest state.  Do not route this through requestLeave(), because its
        # NPCForceAcknowledge check can still see the old trolley quest before
        # those distributed fields reach the client.  Arm the normal teleport
        # transition before allDone tears down the temporary tutorial zones.
        place.fsm.request('teleportOut', [requestStatus])
        messenger.send('stopTutorial')
        return task.done

    def d_allDone(self):
        self.sendUpdate('allDone', [])

    def d_toonArrived(self):
        self.sendUpdate('toonArrived', [])
