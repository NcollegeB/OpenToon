# This module implements the SpeedChat Cog interface, presenting and updating player controls and
# information for SpeedChat menus, terminals, phrases, and decoding.

from otp.speedchat.SCMenu import SCMenu
from otp.speedchat.SCStaticTextTerminal import SCStaticTextTerminal

class TTSCCogMenu(SCMenu):

    def __init__(self, indices):
        SCMenu.__init__(self)
        for index in indices:
            term = SCStaticTextTerminal(index)
            self.append(term)

    def destroy(self):
        SCMenu.destroy(self)
