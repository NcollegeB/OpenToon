"""Global, non-destructive quest-card overlay.

The Shticker Book quest page already knows how to render every supported quest
type.  This overlay uses the same QuestBookPoster widgets without reparenting
the live book page, so Caps Lock remains safe in playgrounds, interiors,
battles, activities, fishing, minigames, and transition states.
"""

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import DirectFrame, DirectLabel
from panda3d.core import TextNode

from otp.otpgui.KeyboardShortcutManager import keyboardShortcutManager
from toontown.quest import QuestBookPoster
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer


def buildQuestSlots(quests, carryLimit, maxSlots):
    """Return every active quest in its display slot, padded with ``None``."""
    limit = max(0, min(int(carryLimit), int(maxSlots)))
    active = [tuple(quest) for quest in list(quests)[:limit]]
    return active + [None] * (maxSlots - len(active))


class QuestOverlay(DirectFrame):
    """A toggleable quest view that is independent of the Shticker Book."""

    def __init__(self, avatar):
        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            sortOrder=75,
        )
        self.avatar = avatar
        self.onscreen = False

        self.backdrop = DirectFrame(
            parent=self,
            relief=DGG.FLAT,
            sortOrder=76,
            frameColor=(0.025, 0.075, 0.14, 0.88),
            frameSize=(-1.2, 1.2, -0.78, 0.78),
        )
        self.backdrop.setBin('fixed', 76)
        self.title = DirectLabel(
            parent=self,
            relief=None,
            sortOrder=78,
            text=TTLocalizer.QuestOverlayTitle,
            text_align=TextNode.ACenter,
            text_scale=0.095,
            text_fg=(1, 0.93, 0.25, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.68),
        )
        self.title.setBin('fixed', 78)
        self.hint = DirectLabel(
            parent=self,
            relief=None,
            sortOrder=78,
            text=TTLocalizer.QuestOverlayHint,
            text_align=TextNode.ACenter,
            text_scale=0.045,
            text_fg=(0.9, 0.95, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, -0.72),
        )
        self.hint.setBin('fixed', 78)
        self.emptyLabel = DirectLabel(
            parent=self,
            relief=None,
            sortOrder=78,
            text=TTLocalizer.QuestOverlayEmpty,
            text_align=TextNode.ACenter,
            text_scale=0.08,
            text_fg=(0.9, 0.95, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0),
        )
        self.emptyLabel.setBin('fixed', 78)

        questPositions = (
            (-0.45, 0, 0.28),
            (-0.45, 0, -0.32),
            (0.45, 0, 0.28),
            (0.45, 0, -0.32),
        )
        self.questFrames = []
        for index in range(ToontownGlobals.MaxQuestCarryLimit):
            frame = QuestBookPoster.QuestBookPoster(
                reverse=index > 1,
                mapIndex=index + 1,
                sortOrder=77,
            )
            # QuestBookPoster consumes its ``parent`` argument without
            # forwarding it to DirectFrame.  Match QuestPage by explicitly
            # reparenting so hiding/destroying this overlay also owns its
            # poster nodes.
            frame.reparentTo(self)
            frame.setBin('fixed', 77)
            frame.setPos(*questPositions[index])
            frame.setScale(1.06)
            frame.setDeleteCallback(None)
            self.questFrames.append(frame)

        self.accept('questsChanged', self.refresh)
        self.accept('questPageUpdated', self.refresh)
        keyboardShortcutManager.registerQuestOverlay(self)
        DirectFrame.hide(self)
        self.refresh()

    def refresh(self):
        quests = list(getattr(self.avatar, 'quests', []))
        try:
            carryLimit = self.avatar.getQuestCarryLimit()
        except (AttributeError, TypeError):
            carryLimit = ToontownGlobals.MaxQuestCarryLimit
        carryLimit = max(
            0,
            min(int(carryLimit), ToontownGlobals.MaxQuestCarryLimit),
        )

        slots = buildQuestSlots(
            quests,
            carryLimit,
            ToontownGlobals.MaxQuestCarryLimit,
        )
        hasActiveQuest = False
        for index, questDesc in enumerate(slots):
            frame = self.questFrames[index]
            frame.clear()
            frame.setDeleteCallback(None)
            if index >= carryLimit:
                frame.mapIndex.hide()
                frame.hide()
                continue
            frame.show()
            if questDesc is None:
                frame.mapIndex.hide()
                continue
            hasActiveQuest = True
            frame.update(questDesc)
            frame.mapIndex.show()

        if hasActiveQuest:
            self.emptyLabel.hide()
        else:
            self.emptyLabel.show()

    def showOverlay(self):
        if self.onscreen:
            return
        self.refresh()
        self.onscreen = True
        DirectFrame.show(self)
        keyboardShortcutManager.registerEscape(
            self,
            self.hideOverlay,
            priority=40,
            slot='quest-overlay',
        )
        messenger.send('wakeup')

    def hideOverlay(self):
        if not self.onscreen:
            return
        self.onscreen = False
        DirectFrame.hide(self)
        keyboardShortcutManager.unregisterEscape(
            self,
            slot='quest-overlay',
        )

    def toggle(self):
        if self.onscreen:
            self.hideOverlay()
        else:
            self.showOverlay()

    def destroy(self):
        self.hideOverlay()
        self.ignoreAll()
        keyboardShortcutManager.unregisterQuestOverlay(self)
        for frame in self.questFrames:
            frame.destroy()
        self.questFrames = []
        self.emptyLabel.destroy()
        self.hint.destroy()
        self.title.destroy()
        self.backdrop.destroy()
        self.avatar = None
        DirectFrame.destroy(self)
