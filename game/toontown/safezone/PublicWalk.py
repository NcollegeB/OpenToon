from panda3d.core import *
from toontown.toonbase.ToontownGlobals import *
from direct.directnotify import DirectNotifyGlobal
from . import Walk
from otp.otpgui.KeyboardShortcutManager import keyboardShortcutManager

class PublicWalk(Walk.Walk):
    notify = DirectNotifyGlobal.directNotify.newCategory('PublicWalk')

    def __init__(self, parentFSM, doneEvent):
        Walk.Walk.__init__(self, doneEvent)
        self.parentFSM = parentFSM

    def load(self):
        Walk.Walk.load(self)

    def unload(self):
        Walk.Walk.unload(self)
        del self.parentFSM

    def enter(self, slowWalk = 0):
        Walk.Walk.enter(self, slowWalk)
        base.localAvatar.book.showButton()
        self.accept(StickerBookHotkey, self.__handleStickerBookEntry)
        self.accept('enterStickerBook', self.__handleStickerBookEntry)
        keyboardShortcutManager.registerEscape(
            self, self.__handleOptionsEntry, priority=0)
        base.localAvatar.laffMeter.start()
        base.localAvatar.beginAllowPies()

    def exit(self):
        Walk.Walk.exit(self)
        base.localAvatar.book.hideButton()
        self.ignore(StickerBookHotkey)
        self.ignore('enterStickerBook')
        keyboardShortcutManager.unregisterEscape(self)
        base.localAvatar.laffMeter.stop()
        base.localAvatar.endAllowPies()

    def __handleStickerBookEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        else:
            doneStatus = {}
            doneStatus['mode'] = 'StickerBook'
            messenger.send(self.doneEvent, [doneStatus])
            return

    def __handleOptionsEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        else:
            doneStatus = {}
            doneStatus['mode'] = 'Options'
            messenger.send(self.doneEvent, [doneStatus])
            return
