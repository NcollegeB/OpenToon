# This module implements the graphics options interface, presenting and updating player controls and
# information for Shticker Book pages, settings, and dialogs.

from direct.fsm import StateData
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import (
    DirectButton,
    DirectFrame,
    DirectLabel,
    DirectOptionMenu,
)
from panda3d.core import TextNode
from toontown.toonbase import ToontownGlobals
from otp.otpgui.KeyboardShortcutManager import keyboardShortcutManager


class GraphicsOptionsDialog(DirectFrame, StateData.StateData):
    """Extended client options with explicit live/restart behavior."""

    FRAME_RATE_CHOICES = (
        ('30 FPS', 30),
        ('60 FPS', 60),
        ('120 FPS', 120),
        ('144 FPS', 144),
        ('Unlimited', 0),
    )
    BOOLEAN_CHOICES = (('Off', False), ('On', True))
    MSAA_CHOICES = (
        ('Off', 0),
        ('2x', 2),
        ('4x', 4),
        ('8x', 8),
    )
    ANISOTROPY_CHOICES = (
        ('Off', 1),
        ('2x', 2),
        ('4x', 4),
        ('8x', 8),
        ('16x', 16),
    )
    VOLUME_CHOICES = tuple(
        ('%s%%' % value, value / 100.0)
        for value in (0, 10, 20, 30, 40, 50, 60, 65, 70, 80, 90, 100)
    )
    FOV_CHOICES = (
        ('45 degrees', 45.0),
        ('52 degrees', 52.0),
        ('60 degrees', 60.0),
        ('70 degrees', 70.0),
        ('80 degrees', 80.0),
        ('90 degrees', 90.0),
    )

    def __init__(self):
        DirectFrame.__init__(
            self,
            pos=(0, 0, 0.1),
            relief=None,
            image=DGG.getDefaultDialogGeom(),
            image_scale=(1.75, 1, 1.45),
            image_pos=(0, 0, -0.06),
            image_color=ToontownGlobals.GlobalDialogColor,
            text='Advanced Settings',
            text_scale=0.11,
            text_pos=(0, 0.56),
            borderWidth=(0.01, 0.01),
        )
        StateData.StateData.__init__(self, 'graphics-options-done')
        self.setBin('gui-popup', 0)
        self.initialiseoptions(GraphicsOptionsDialog)

    def load(self):
        if self.isLoaded:
            return
        self.isLoaded = 1
        self._labels = []
        self._menus = {}
        self._choices = {}

        rows = (
            ('fps-limit', 'Frame-rate limit', self.FRAME_RATE_CHOICES),
            ('show-fps', 'Show FPS meter', self.BOOLEAN_CHOICES),
            ('vsync', 'Vertical sync', self.BOOLEAN_CHOICES),
            ('msaa', 'Anti-aliasing (MSAA)', self.MSAA_CHOICES),
            ('anisotropy', 'Texture filtering', self.ANISOTROPY_CHOICES),
            ('music-volume', 'Music volume', self.VOLUME_CHOICES),
            ('sfx-volume', 'Sound effects volume', self.VOLUME_CHOICES),
            ('particles', 'Particle effects', self.BOOLEAN_CHOICES),
            ('fov', 'Camera field of view', self.FOV_CHOICES),
        )
        startY = 0.39
        rowHeight = 0.095
        for index, (key, labelText, choices) in enumerate(rows):
            y = startY - index * rowHeight
            label = DirectLabel(
                parent=self,
                relief=None,
                text=labelText,
                text_align=TextNode.ALeft,
                text_scale=0.052,
                pos=(-0.73, 0, y),
            )
            menu = DirectOptionMenu(
                parent=self,
                relief=DGG.RAISED,
                items=[choice[0] for choice in choices],
                initialitem=choices[0][0],
                scale=0.052,
                text_align=TextNode.ALeft,
                pos=(0.18, 0, y),
                popupMarker_pos=(3.6, 0, 0),
                highlightColor=(0.65, 0.85, 1.0, 1.0),
            )
            self._labels.append(label)
            self._menus[key] = menu
            self._choices[key] = choices

        self.statusLabel = DirectLabel(
            parent=self,
            relief=None,
            text='VSync, MSAA, and texture filtering apply next launch.',
            text_scale=0.045,
            text_wordwrap=31,
            pos=(0, 0, -0.49),
        )

        buttonGui = loader.loadModel('phase_3/models/gui/quit_button')
        buttonImages = (
            buttonGui.find('**/QuitBtn_UP'),
            buttonGui.find('**/QuitBtn_DN'),
            buttonGui.find('**/QuitBtn_RLVR'),
        )
        self.applyButton = DirectButton(
            parent=self,
            relief=None,
            image=buttonImages,
            image_scale=(0.75, 1, 1),
            text='Apply',
            text_scale=0.06,
            text_pos=(0, -0.02),
            pos=(-0.36, 0, -0.65),
            command=self._apply,
        )
        self.closeButton = DirectButton(
            parent=self,
            relief=None,
            image=buttonImages,
            image_scale=(0.75, 1, 1),
            text='Close',
            text_scale=0.06,
            text_pos=(0, -0.02),
            pos=(0.36, 0, -0.65),
            command=self.exit,
        )
        buttonGui.removeNode()
        self.hide()

    def enter(self):
        if not StateData.StateData.enter(self):
            return
        self._loadValues()
        self.statusLabel['text'] = (
            'VSync, MSAA, and texture filtering apply next launch.')
        self.show()
        keyboardShortcutManager.registerEscape(
            self, self.exit, priority=80)

    def exit(self):
        if not StateData.StateData.exit(self):
            return
        keyboardShortcutManager.unregisterEscape(self)
        self.hide()
        messenger.send(self.doneEvent)

    def unload(self):
        if not self.isLoaded:
            return
        if self.isEntered:
            self.exit()
        for label in self._labels:
            label.destroy()
        for menu in self._menus.values():
            menu.destroy()
        self.applyButton.destroy()
        self.closeButton.destroy()
        self.statusLabel.destroy()
        self._labels = []
        self._menus = {}
        self._choices = {}
        self.isLoaded = 0
        DirectFrame.destroy(self)

    def _displayForValue(self, key, value, default):
        choices = self._choices[key]
        for display, candidate in choices:
            if candidate == value:
                return display
        for display, candidate in choices:
            if candidate == default:
                return display
        return choices[0][0]

    def _valueForDisplay(self, key):
        selected = self._menus[key].get()
        for display, value in self._choices[key]:
            if display == selected:
                return value
        return self._choices[key][0][1]

    def _loadValues(self):
        defaults = {
            'fps-limit': 60,
            'show-fps': False,
            'vsync': True,
            'msaa': 0,
            'anisotropy': 8,
            'music-volume': 0.65,
            'sfx-volume': 1.0,
            'particles': True,
            'fov': 52.0,
        }
        for key, default in defaults.items():
            value = base.settings.getSetting(key, default)
            display = self._displayForValue(key, value, default)
            self._menus[key].set(display, fCommand=0)

    def _apply(self):
        previousRestartValues = {
            key: base.settings.getSetting(key, default)
            for key, default in (
                ('vsync', True),
                ('msaa', 0),
                ('anisotropy', 8),
            )
        }
        for key in self._menus:
            base.settings.updateSetting(key, self._valueForDisplay(key))
        base.settings.writeSettings()

        if hasattr(base, 'applyRuntimeSettings'):
            base.applyRuntimeSettings()

        restartRequired = any(
            previousRestartValues[key] != base.settings.getSetting(key)
            for key in previousRestartValues
        )
        if restartRequired:
            self.statusLabel['text'] = (
                'Saved. Restart the client to apply VSync, MSAA, or '
                'texture filtering changes.')
        else:
            self.statusLabel['text'] = 'Saved and applied.'
