# This module defines Toontown SpeedChat relay and its supporting behavior for global delivery,
# party, mail, news, whitelist, and data services.

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.otpbase import OTPGlobals
from otp.uberdog.SpeedchatRelay import SpeedchatRelay
from otp.uberdog import SpeedchatRelayGlobals

class TTSpeedchatRelay(SpeedchatRelay):

    def __init__(self, cr):
        SpeedchatRelay.__init__(self, cr)

    def sendSpeedchatToonTask(self, receiverId, taskId, toNpcId, toonProgress, msgIndex):
        self.sendSpeedchatToRelay(receiverId, SpeedchatRelayGlobals.TOONTOWN_QUEST, [taskId,
         toNpcId,
         toonProgress,
         msgIndex])
