# This module implements the tailor clothes interface, presenting and updating player controls and
# information for player Toon avatars, NPCs, inventory, and presentation.

from toontown.makeatoon import ClothesGUI
from . import ToonDNA

class TailorClothesGUI(ClothesGUI.ClothesGUI):
    notify = directNotify.newCategory('MakeClothesGUI')

    def __init__(self, doneEvent, swapEvent, tailorId):
        ClothesGUI.ClothesGUI.__init__(self, ClothesGUI.CLOTHES_TAILOR, doneEvent, swapEvent)
        self.tailorId = tailorId

    def setupScrollInterface(self):
        self.dna = self.toon.getStyle()
        gender = self.dna.getGender()
        if self.swapEvent != None:
            self.tops = ToonDNA.getTops(gender, tailorId=self.tailorId)
            self.bottoms = ToonDNA.getBottoms(gender, tailorId=self.tailorId)
            self.gender = gender
            self.topChoice = -1
            self.bottomChoice = -1
        self.setupButtons()
        return
