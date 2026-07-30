# This module defines SpeedChat resistance terminal and its supporting behavior for SpeedChat menus,
# terminals, phrases, and decoding.

from otp.speedchat.SCTerminal import SCTerminal
from toontown.chat import ResistanceChat
TTSCResistanceMsgEvent = 'TTSCResistanceMsg'

def decodeTTSCResistanceMsg(textId):
    return ResistanceChat.getChatText(textId)


class TTSCResistanceTerminal(SCTerminal):

    def __init__(self, textId, charges):
        SCTerminal.__init__(self)
        self.setCharges(charges)
        self.textId = textId
        self.text = ResistanceChat.getItemText(self.textId)

    def isWhisperable(self):
        return False

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(TTSCResistanceMsgEvent), [self.textId])
