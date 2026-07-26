"""Source checks for the repeatable live minigame client harness."""

import ast
from pathlib import Path
import unittest


GAME_ROOT = Path(__file__).resolve().parents[1]
CLIENT_PATH = GAME_ROOT / 'tools/live_minigame_client.py'
STARTER_PATH = GAME_ROOT / 'tools/start_live_minigame_clients.ps1'


class LiveMinigameHarnessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.clientSource = CLIENT_PATH.read_text(encoding='utf-8')
        cls.starterSource = STARTER_PATH.read_text(encoding='utf-8')
        ast.parse(cls.clientSource, CLIENT_PATH)

    def test_client_uses_slot_zero_and_unique_window_configuration(self):
        self.assertIn('auto-avatar-choice %s', self.clientSource)
        self.assertIn('window-title %s', self.clientSource)
        self.assertIn('win-origin %s %s', self.clientSource)
        self.assertIn(
            'properties.setSize(options.width, options.height)',
            self.clientSource)
        self.assertIn(
            'properties.setOrigin(options.x, options.y)',
            self.clientSource)

    def test_client_adds_the_game_root_to_its_import_path(self):
        self.assertIn(
            "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
            self.clientSource)
        self.assertIn("sys.path.insert(0, GAME_ROOT)", self.clientSource)

    def test_each_client_uses_a_persistent_log_file(self):
        self.assertIn("parser.add_argument('--log-file'", self.clientSource)
        self.assertIn('sys.stdout = logStream', self.clientSource)
        self.assertIn('sys.stderr = logStream', self.clientSource)
        self.assertIn('sys.__stdout__ = logStream', self.clientSource)
        self.assertIn('sys.__stderr__ = logStream', self.clientSource)
        self.assertIn(
            '"live-minigame-client-$number.log"',
            self.starterSource)

    def test_trolley_boarding_enters_the_local_activity_first(self):
        enterIndex = self.clientSource.index(
            'place.detectedTrolleyCollision()')
        boardIndex = self.clientSource.index(
            "trolley.sendUpdate('requestBoard', [])")
        self.assertLess(enterIndex, boardIndex)

    def test_completed_quest_popups_are_dismissed_before_boarding(self):
        dismissIndex = self.clientSource.index(
            "if placeState == 'popup':")
        boardIndex = self.clientSource.index(
            "trolley.sendUpdate('requestBoard', [])")
        self.assertIn("messenger.send('escape')", self.clientSource)
        self.assertLess(dismissIndex, boardIndex)

    def test_only_the_first_client_forces_the_requested_game(self):
        self.assertIn(
            'if ($index -eq 0 -and $Minigame)',
            self.starterSource)
        self.assertIn(
            "$arguments += @('--minigame', $Minigame)",
            self.starterSource)

    def test_starter_rejects_duplicate_tokens(self):
        self.assertIn(
            '($Tokens | Select-Object -Unique).Count',
            self.starterSource)
        self.assertIn(
            'Every live client must use a distinct local account token.',
            self.starterSource)


if __name__ == '__main__':
    unittest.main(verbosity=2)
