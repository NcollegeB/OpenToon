"""Focused regression tests for Race Game early-exit cleanup."""

import ast
from pathlib import Path
import unittest


GAME_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = (
    GAME_ROOT / 'toontown/minigame/DistributedRaceGame.py')


class RaceCleanupTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE_PATH.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source, SOURCE_PATH)
        cls.raceClass = next(
            node for node in cls.tree.body
            if isinstance(node, ast.ClassDef) and
            node.name == 'DistributedRaceGame')

    def _method_source(self, methodName):
        method = next(
            node for node in self.raceClass.body
            if isinstance(node, ast.FunctionDef) and
            node.name == methodName)
        return ast.get_source_segment(self.source, method)

    def test_owned_intervals_are_paused_before_nodes_are_removed(self):
        stopSource = self._method_source('__stopRaceMotion')
        self.assertIn(
            "self.__pauseRaceInterval('chanceCardInterval')",
            stopSource)
        self.assertIn(
            "self.__pauseRaceInterval('cameraInterval')",
            stopSource)
        self.assertIn('track.pause()', stopSource)
        unloadSource = self._method_source('unload')
        self.assertLess(
            unloadSource.index('self.__stopRaceMotion()'),
            unloadSource.index('self.raceBoard.removeNode()'))

    def test_every_early_exit_path_stops_race_motion(self):
        for methodName in (
                'exitMoveAvatars',
                'enterCleanup',
                'offstage',
                'unload'):
            self.assertIn(
                'self.__stopRaceMotion()',
                self._method_source(methodName),
                methodName)

    def test_delayed_tasks_and_intervals_use_instance_names(self):
        self.assertNotIn("taskMgr.add(moveTask, 'moveAvatars')", self.source)
        self.assertNotIn(
            "taskMgr.doMethodLater(4.0, self.gameOverCallback, 'playMovie')",
            self.source)
        self.assertIn("self.uniqueName('moveAvatars')", self.source)
        self.assertIn("self.uniqueName('playMovie')", self.source)
        self.assertIn("self.uniqueName('cardLerp')", self.source)
        self.assertIn("self.uniqueName('cameraLerp')", self.source)

    def test_avatar_tracks_are_paused_not_finished_during_teardown(self):
        stopSource = self._method_source('__stopRaceMotion')
        self.assertIn('track.pause()', stopSource)
        self.assertNotIn('track.finish()', stopSource)
        self.assertIn("avatar.setAnimState('neutral', 1.0)", stopSource)

    def test_pending_dice_nodes_are_removed_idempotently(self):
        hideSource = self._method_source('hideNumbers')
        stopSource = self._method_source('__stopRaceMotion')
        self.assertIn(
            "getattr(self, 'diceInstanceList', [])",
            hideSource)
        self.assertIn(
            "getattr(self, 'diceInstanceList', [])",
            stopSource)
        self.assertIn('self.diceInstanceList = []', stopSource)


if __name__ == '__main__':
    unittest.main(verbosity=2)
