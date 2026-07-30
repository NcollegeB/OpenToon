# This module defines paint mixer and its supporting behavior for Cog HQ facilities, bosses, rooms,
# and level entities.

from . import PlatformEntity

class PaintMixer(PlatformEntity.PlatformEntity):

    def start(self):
        PlatformEntity.PlatformEntity.start(self)
        model = self.platform.model
        shaft = model.find('**/PaintMixerBase1')
        shaft.setSz(self.shaftScale)
        shaft.node().setPreserveTransform(0)
        shaftChild = shaft.find('**/PaintMixerBase')
        shaftChild.node().setPreserveTransform(0)
        model.flattenMedium()
