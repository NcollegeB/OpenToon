"""Central keyboard routing for modal UI, quests, and paged conversations.

Historically, several client states listened to ``escape`` independently.
That made one key press capable of both dismissing a popup and opening or
closing the Shticker Book.  This manager gives modal dialogs first refusal,
then invokes only the highest-priority active menu/game callback.  It also
keeps the Caps Lock quest overlay available for the lifetime of the local
avatar instead of tying it to one walk state.
"""

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectDialog import DirectDialog
from direct.gui.DirectGuiBase import DirectGuiWidget
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from panda3d.core import PGEntry, PGItem


class KeyboardShortcutManager(DirectObject):
    """Route shared keyboard shortcuts to the active client context."""

    notify = DirectNotifyGlobal.directNotify.newCategory(
        'KeyboardShortcutManager')

    def __init__(self):
        DirectObject.__init__(self)
        self._serial = 0
        self._escapeCallbacks = {}
        self._dialogueCallbacks = {}
        self._questOverlay = None
        self._suspendedBackgroundEntries = {}
        self.accept('escape', self._handleEscape)
        self.accept('space', self._handleSpace)
        self.accept('caps_lock', self._handleQuestOverlay)

    def registerEscape(self, owner, callback, priority=0, once=False,
                       slot='default'):
        """Register or replace an Escape action for an active context."""
        self._serial += 1
        key = (id(owner), slot)
        self._escapeCallbacks[key] = (
            owner, callback, priority, self._serial, once)

    def unregisterEscape(self, owner, slot='default'):
        self._escapeCallbacks.pop((id(owner), slot), None)

    def registerDialogue(self, owner, callback):
        """Make Space advance the most recently activated page dialogue."""
        if not self._dialogueCallbacks:
            self._suspendBackgroundTextEntries()
        self._serial += 1
        self._dialogueCallbacks[id(owner)] = (
            owner, callback, 0, self._serial, False)

    def unregisterDialogue(self, owner):
        self._dialogueCallbacks.pop(id(owner), None)
        if not self._dialogueCallbacks:
            self._restoreBackgroundTextEntries()

    def registerQuestOverlay(self, overlay):
        """Register the current local avatar's global quest overlay."""
        self._questOverlay = overlay

    def unregisterQuestOverlay(self, overlay):
        if self._questOverlay is overlay:
            self._questOverlay = None

    def _handleEscape(self):
        # A visible modal always wins over menus and gameplay escape actions.
        if self.dismissTopDialog():
            return
        self._invokeNewest(self._escapeCallbacks)

    def _handleSpace(self):
        # A focused name, password, code, or chat field owns printable keys.
        # Background-focus chat entries are suspended while page dialogue is
        # active, but this check also protects entries activated afterward.
        if self._textEntryHasFocus():
            return
        self._invokeNewest(self._dialogueCallbacks)

    def _handleQuestOverlay(self):
        overlay = self._questOverlay
        if overlay is None:
            return
        # Caps Lock still belongs to a foreground name, code, password, or
        # chat field.  Do not treat background-focus chat as foreground here;
        # normal gameplay keeps that entry armed even when the player is not
        # actively typing.
        if self._foregroundTextEntryHasFocus():
            return
        try:
            overlay.toggle()
        except (AttributeError, TypeError) as error:
            # Avatar teardown can overlap one final queued key event.
            self.notify.warning(
                'Quest overlay toggle failed during teardown: %s' % error)
            self._questOverlay = None

    @staticmethod
    def _iterTextEntries():
        for widget in list(DirectGuiWidget.guiDict.values()):
            guiItem = getattr(widget, 'guiItem', None)
            if isinstance(guiItem, PGEntry):
                yield widget, guiItem

    @classmethod
    def _textEntryHasFocus(cls):
        if isinstance(PGItem.getFocusItem(), PGEntry):
            return True
        return any(
            guiItem.getBackgroundFocus()
            for widget, guiItem in cls._iterTextEntries())

    @classmethod
    def _foregroundTextEntryHasFocus(cls):
        focusItem = PGItem.getFocusItem()
        if not isinstance(focusItem, PGEntry):
            return False
        for widget, guiItem in cls._iterTextEntries():
            if (guiItem != focusItem and
                    guiItem.getName() != focusItem.getName()):
                continue
            try:
                if widget.isHidden():
                    return False
                # DirectEntry keeps the requested background-focus option even
                # when its native PGEntry temporarily reports ordinary focus.
                return not bool(widget['backgroundFocus'])
            except (AttributeError, KeyError, TypeError):
                break
        return not focusItem.getBackgroundFocus()

    def _suspendBackgroundTextEntries(self):
        for widget, guiItem in self._iterTextEntries():
            if guiItem.getBackgroundFocus():
                # Change only the native state.  Keeping the DirectEntry
                # option intact lets us detect whether its owner intentionally
                # disabled background focus before dialogue ended.
                guiItem.setBackgroundFocus(False)
                self._suspendedBackgroundEntries[id(widget)] = widget

    def _restoreBackgroundTextEntries(self):
        for widget in list(self._suspendedBackgroundEntries.values()):
            try:
                if (not widget.isEmpty() and
                        widget['backgroundFocus']):
                    widget.guiItem.setBackgroundFocus(True)
            except (AttributeError, KeyError, TypeError):
                pass
        self._suspendedBackgroundEntries.clear()

    def _invokeNewest(self, callbacks):
        if not callbacks:
            return False
        key, entry = max(
            callbacks.items(),
            key=lambda item: (item[1][2], item[1][3]))
        owner, callback, priority, serial, once = entry
        if once:
            callbacks.pop(key, None)
        callback()
        return True

    @staticmethod
    def _dismissValue(dialog):
        """Choose the non-destructive button represented by Escape."""
        try:
            values = list(dialog['buttonValueList'])
        except (KeyError, TypeError):
            values = []
        if DGG.DIALOG_CANCEL in values:
            return DGG.DIALOG_CANCEL
        if DGG.DIALOG_NO in values:
            return DGG.DIALOG_NO
        if len(values) == 1:
            return values[0]
        return None

    @staticmethod
    def _dialogSort(dialog):
        try:
            return int(dialog.getSort())
        except (AttributeError, TypeError, ValueError):
            try:
                return int(dialog['sortOrder'])
            except (KeyError, TypeError, ValueError):
                return 0

    def dismissTopDialog(self):
        """Dismiss the newest visible DirectDialog, if it is dismissible."""
        # Sort order determines which dialog is drawn above another.  Creation
        # order is the deterministic tie-breaker used by overlapping modals.
        dialogs = list(DirectDialog.AllDialogs.values())
        rankedDialogs = sorted(
            enumerate(dialogs),
            key=lambda item: (self._dialogSort(item[1]), item[0]),
            reverse=True)
        for creationIndex, dialog in rankedDialogs:
            try:
                if dialog.isEmpty() or dialog.isHidden():
                    continue
                if not dialog['command'] or not dialog.buttonList:
                    continue
            except (AttributeError, KeyError, TypeError):
                continue
            value = self._dismissValue(dialog)
            if value is None:
                continue
            dialog.buttonCommand(value)
            return True
        return False

    def _resetForTests(self):
        """Clear dynamic registrations without removing global key bindings."""
        self._escapeCallbacks.clear()
        self._restoreBackgroundTextEntries()
        self._dialogueCallbacks.clear()
        self._questOverlay = None


keyboardShortcutManager = KeyboardShortcutManager()
