"""Focused offscreen verification for the global Caps Lock quest overlay."""

import pathlib
import os
import sys

GAME_ROOT = pathlib.Path(__file__).resolve().parents[1]
RESOURCE_ROOT = GAME_ROOT / 'resources'
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from panda3d.core import Filename, loadPrcFileData

loadPrcFileData('', 'window-type offscreen')
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'sync-video false')
loadPrcFileData('', 'model-path %s' % RESOURCE_ROOT.as_posix())
loadPrcFileData('', 'default-model-extension .bam')

from direct.showbase.ShowBase import ShowBase
from direct.showbase.MessengerGlobal import messenger


class _Avatar:
    def __init__(self):
        # Stinky's live completed tutorial quest exercises the real poster
        # renderer instead of only the empty-state path.
        self.quests = [[145, 1000, 1000, 100, 1]]

    @staticmethod
    def getQuestCarryLimit():
        return 4


def main():
    game = ShowBase()
    from toontown.quest.QuestOverlay import QuestOverlay
    from toontown.quest.QuestOverlay import buildQuestSlots

    avatar = _Avatar()
    game.localAvatar = avatar

    slots = buildQuestSlots(
        [
            [101, 2001, 2002, 100, 0],
            [102, 2001, 2002, 101, 1],
            [103, 2001, 2002, 102, 2],
            [104, 2001, 2002, 103, 3],
        ],
        4,
        4,
    )
    assert len(slots) == 4
    assert [slot[0] for slot in slots] == [101, 102, 103, 104]

    overlay = QuestOverlay(avatar)
    assert not overlay.onscreen
    assert all(frame.getParent() == overlay for frame in overlay.questFrames)
    messenger.send('caps_lock')
    assert overlay.onscreen
    assert not overlay.isHidden()
    assert overlay.backdrop.getBinName() == 'fixed'
    assert overlay.backdrop.getBinDrawOrder() == 76
    assert overlay.questFrames[0].getBinName() == 'fixed'
    assert overlay.questFrames[0].getBinDrawOrder() == 77
    screenshotPath = os.environ.get('QUEST_OVERLAY_SCREENSHOT')
    if screenshotPath:
        game.graphicsEngine.renderFrame()
        game.graphicsEngine.renderFrame()
        assert game.win.saveScreenshot(
            Filename.fromOsSpecific(screenshotPath))
    messenger.send('escape')
    assert not overlay.onscreen
    assert overlay.isHidden()
    messenger.send('caps_lock')
    assert overlay.onscreen
    messenger.send('caps_lock')
    assert not overlay.onscreen

    overlay.destroy()
    game.destroy()
    print('QUEST_OVERLAY_OK slots=4 caps_toggle=2 escape_close=1')


if __name__ == '__main__':
    main()
