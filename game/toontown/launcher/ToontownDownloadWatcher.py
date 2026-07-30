# This module defines Toontown download watcher and its supporting behavior for client startup,
# downloading, and launch monitoring.

from direct.directnotify import DirectNotifyGlobal
from otp.launcher.DownloadWatcher import DownloadWatcher
from toontown.toonbase import TTLocalizer

class ToontownDownloadWatcher(DownloadWatcher):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDownloadWatcher')

    def __init__(self, phaseNames):
        DownloadWatcher.__init__(self, phaseNames)

    def update(self, phase, percent, reqByteRate, actualByteRate):
        DownloadWatcher.update(self, phase, percent, reqByteRate, actualByteRate)
        phaseName = self.phaseNames[phase]
        self.text['text'] = TTLocalizer.LoadingDownloadWatcherUpdate % phaseName
