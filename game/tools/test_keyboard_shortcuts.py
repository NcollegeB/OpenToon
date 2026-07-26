"""Focused tests for Escape, Space, and Caps Lock shortcut routing.

Run with the bundled game interpreter:
    ..\runtime\Panda3D-1.11.0-x64\python\ppython.exe \
        tools\test_keyboard_shortcuts.py
"""

import pathlib
import sys
import unittest

GAME_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectDialog import DirectDialog
from direct.gui.DirectGuiBase import DirectGuiWidget
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import PGEntry

from otp.otpgui.KeyboardShortcutManager import keyboardShortcutManager


class _Owner:
    pass


class _FakeDialog:
    def __init__(self, values, result, hidden=False, command=True, sort=0):
        self._values = values
        self._result = result
        self._hidden = hidden
        self._command = command
        self._sort = sort
        self.buttonList = [object()] if values else []

    def __getitem__(self, key):
        if key == 'buttonValueList':
            return self._values
        if key == 'command':
            return self._command
        raise KeyError(key)

    def isEmpty(self):
        return False

    def isHidden(self):
        return self._hidden

    def getSort(self):
        return self._sort

    def buttonCommand(self, value):
        self._result.append(value)


class _FakeEntry:
    def __init__(self, backgroundFocus=False, hidden=False):
        self.guiItem = PGEntry('test-entry')
        self._backgroundFocus = backgroundFocus
        self._hidden = hidden
        self.guiItem.setBackgroundFocus(backgroundFocus)

    def __getitem__(self, key):
        if key == 'backgroundFocus':
            return self._backgroundFocus
        raise KeyError(key)

    def isEmpty(self):
        return False

    def isHidden(self):
        return self._hidden


class _FakeQuestOverlay:
    def __init__(self):
        self.toggleCount = 0

    def toggle(self):
        self.toggleCount += 1


class KeyboardShortcutManagerTests(unittest.TestCase):
    def setUp(self):
        keyboardShortcutManager._resetForTests()
        self._dialogs = DirectDialog.AllDialogs
        DirectDialog.AllDialogs = {}

    def tearDown(self):
        keyboardShortcutManager._resetForTests()
        DirectDialog.AllDialogs = self._dialogs

    def test_escape_dismisses_modal_before_menu_callback(self):
        menuCalls = []
        dialogCalls = []
        owner = _Owner()
        keyboardShortcutManager.registerEscape(
            owner, lambda: menuCalls.append('menu'))
        DirectDialog.AllDialogs['active'] = _FakeDialog(
            [DGG.DIALOG_OK, DGG.DIALOG_CANCEL], dialogCalls)

        messenger.send('escape')

        self.assertEqual(dialogCalls, [DGG.DIALOG_CANCEL])
        self.assertEqual(menuCalls, [])

    def test_escape_uses_highest_priority_active_context(self):
        calls = []
        lowOwner = _Owner()
        highOwner = _Owner()
        keyboardShortcutManager.registerEscape(
            lowOwner, lambda: calls.append('low'), priority=0)
        keyboardShortcutManager.registerEscape(
            highOwner, lambda: calls.append('high'), priority=50)

        messenger.send('escape')
        keyboardShortcutManager.unregisterEscape(highOwner)
        messenger.send('escape')

        self.assertEqual(calls, ['high', 'low'])

    def test_escape_chooses_no_and_acknowledge_safely(self):
        noCalls = []
        DirectDialog.AllDialogs['yes-no'] = _FakeDialog(
            [DGG.DIALOG_YES, DGG.DIALOG_NO], noCalls)
        messenger.send('escape')
        self.assertEqual(noCalls, [DGG.DIALOG_NO])

        DirectDialog.AllDialogs = {
            'acknowledge': _FakeDialog([DGG.DIALOG_OK], noCalls)}
        messenger.send('escape')
        self.assertEqual(noCalls, [DGG.DIALOG_NO, DGG.DIALOG_OK])

    def test_escape_dismisses_highest_visible_dialog_deterministically(self):
        olderCalls = []
        newerCalls = []
        topCalls = []
        DirectDialog.AllDialogs['older'] = _FakeDialog(
            [DGG.DIALOG_OK], olderCalls, sort=10)
        DirectDialog.AllDialogs['newer-same-sort'] = _FakeDialog(
            [DGG.DIALOG_OK], newerCalls, sort=10)
        DirectDialog.AllDialogs['top-sort'] = _FakeDialog(
            [DGG.DIALOG_OK], topCalls, sort=20)

        messenger.send('escape')

        self.assertEqual(olderCalls, [])
        self.assertEqual(newerCalls, [])
        self.assertEqual(topCalls, [DGG.DIALOG_OK])

    def test_space_advances_only_newest_active_dialogue(self):
        calls = []
        first = _Owner()
        second = _Owner()
        keyboardShortcutManager.registerDialogue(
            first, lambda: calls.append('first'))
        keyboardShortcutManager.registerDialogue(
            second, lambda: calls.append('second'))

        messenger.send('space')
        keyboardShortcutManager.unregisterDialogue(second)
        messenger.send('space')

        self.assertEqual(calls, ['second', 'first'])

    def test_space_respects_focused_text_entry(self):
        calls = []
        owner = _Owner()
        entry = PGEntry('focused-test-entry')
        entry.setFocus(True)
        try:
            keyboardShortcutManager.registerDialogue(
                owner, lambda: calls.append('dialogue'))
            messenger.send('space')
        finally:
            entry.setFocus(False)

        self.assertEqual(calls, [])

    def test_dialogue_temporarily_suspends_background_chat_entry(self):
        calls = []
        owner = _Owner()
        entry = _FakeEntry(backgroundFocus=True)
        DirectGuiWidget.guiDict['test-background-entry'] = entry
        try:
            keyboardShortcutManager.registerDialogue(
                owner, lambda: calls.append('dialogue'))
            self.assertFalse(entry.guiItem.getBackgroundFocus())
            messenger.send('space')
            keyboardShortcutManager.unregisterDialogue(owner)
            self.assertTrue(entry.guiItem.getBackgroundFocus())
        finally:
            DirectGuiWidget.guiDict.pop('test-background-entry', None)

        self.assertEqual(calls, ['dialogue'])

    def test_caps_lock_toggles_registered_quest_overlay(self):
        overlay = _FakeQuestOverlay()
        keyboardShortcutManager.registerQuestOverlay(overlay)

        messenger.send('caps_lock')
        messenger.send('caps_lock')

        self.assertEqual(overlay.toggleCount, 2)

    def test_caps_lock_respects_foreground_text_entry(self):
        overlay = _FakeQuestOverlay()
        entry = PGEntry('focused-caps-entry')
        keyboardShortcutManager.registerQuestOverlay(overlay)
        entry.setFocus(True)
        try:
            messenger.send('caps_lock')
        finally:
            entry.setFocus(False)

        self.assertEqual(overlay.toggleCount, 0)

    def test_caps_lock_ignores_background_chat_focus(self):
        overlay = _FakeQuestOverlay()
        entry = _FakeEntry(backgroundFocus=True, hidden=True)
        keyboardShortcutManager.registerQuestOverlay(overlay)
        DirectGuiWidget.guiDict['caps-background-entry'] = entry
        # The live SpeedChat DirectEntry can be the native focus item while
        # reporting false here; its DirectEntry option is authoritative.
        entry.guiItem.setBackgroundFocus(False)
        entry.guiItem.setFocus(True)
        try:
            messenger.send('caps_lock')
        finally:
            entry.guiItem.setFocus(False)
            DirectGuiWidget.guiDict.pop('caps-background-entry', None)

        self.assertEqual(overlay.toggleCount, 1)

    def test_caps_lock_is_safe_without_a_local_quest_overlay(self):
        overlay = _FakeQuestOverlay()
        keyboardShortcutManager.registerQuestOverlay(overlay)
        keyboardShortcutManager.unregisterQuestOverlay(overlay)

        messenger.send('caps_lock')

        self.assertEqual(overlay.toggleCount, 0)


if __name__ == '__main__':
    unittest.main()
