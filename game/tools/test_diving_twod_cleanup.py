"""Focused source regressions for minigame early-exit cleanup."""

import ast
from pathlib import Path
import unittest


GAME_ROOT = Path(__file__).resolve().parents[1]
MINIGAME_ROOT = GAME_ROOT / 'toontown/minigame'


def _load_class(fileName, className):
    sourcePath = MINIGAME_ROOT / fileName
    source = sourcePath.read_text(encoding='utf-8')
    tree = ast.parse(source, sourcePath)
    sourceClass = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == className)
    return sourcePath, source, sourceClass


def _load_method(fileName, className, methodName):
    sourcePath, source, sourceClass = _load_class(fileName, className)
    method = next(
        node for node in sourceClass.body
        if isinstance(node, ast.FunctionDef) and node.name == methodName)
    return sourcePath, source, method


def _method_text(fileName, className, methodName):
    sourcePath, source, method = _load_method(
        fileName, className, methodName)
    text = ast.get_source_segment(source, method)
    if text is None:
        raise AssertionError(
            'Could not read %s.%s from %s' %
            (className, methodName, sourcePath))
    return text


def _class_string_constant(fileName, className, constantName):
    sourcePath, unusedSource, sourceClass = _load_class(
        fileName, className)
    for node in sourceClass.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == constantName:
            return ast.literal_eval(node.value)
    raise AssertionError(
        'Could not find %s.%s in %s' %
        (className, constantName, sourcePath))


class DivingCleanupTests(unittest.TestCase):

    def test_offstage_removes_both_local_collision_nodes(self):
        unusedPath, unusedSource, method = _load_method(
            'DistributedDivingGame.py',
            'DistributedDivingGame',
            'offstage')
        guardedFields = []
        for node in ast.walk(method):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != 'hasattr':
                continue
            if len(node.args) != 2:
                continue
            field = node.args[1]
            if isinstance(field, ast.Constant) and isinstance(field.value, str):
                guardedFields.append(field.value)

        self.assertIn('cSphereNodePath1', guardedFields)
        self.assertIn('cSphereNodePath2', guardedFields)
        methodText = _method_text(
            'DistributedDivingGame.py',
            'DistributedDivingGame',
            'offstage')
        self.assertIn(
            'self.cTrav.removeCollider(self.cSphereNodePath1)',
            methodText)
        self.assertIn(
            'self.cTrav2.removeCollider(self.cSphereNodePath2)',
            methodText)
        self.assertIn(
            'self.pusher.removeCollider(self.cSphereNodePath1)',
            methodText)

    def test_remote_collision_nodes_have_distinct_keys(self):
        methodText = _method_text(
            'DistributedDivingGame.py',
            'DistributedDivingGame',
            'setGameReady')
        self.assertIn(
            "int(str(avId) + str(1))",
            methodText)
        self.assertIn(
            "int(str(avId) + str(2))",
            methodText)

    def test_both_local_collision_nodes_use_the_diving_mask(self):
        methodText = _method_text(
            'DistributedDivingGame.py',
            'DistributedDivingGame',
            'setGameReady')
        self.assertEqual(
            methodText.count(
                'cSphereNode.setFromCollideMask('
                'DivingGameGlobals.CollideMask)'),
            2)

    def test_exit_swim_destroys_every_map_avatar(self):
        methodText = _method_text(
            'DistributedDivingGame.py',
            'DistributedDivingGame',
            'exitSwim')
        self.assertIn(
            'for mapAvatar in list(self.mapAvatars.values()):',
            methodText)
        self.assertIn('mapAvatar.destroy()', methodText)
        self.assertNotIn(
            'self.mapAvatars[self.localAvId].destroy()',
            methodText)


class TwoDCleanupTests(unittest.TestCase):

    def test_exit_play_stops_update_task_and_enemy_event(self):
        methodText = _method_text(
            'DistributedTwoDGame.py',
            'DistributedTwoDGame',
            'exitPlay')
        self.assertIn(
            'taskMgr.remove(self.UpdateLocalToonTask)',
            methodText)
        self.assertIn("self.ignore('enemyShot')", methodText)

    def test_cleanup_stops_update_task_idempotently(self):
        methodText = _method_text(
            'DistributedTwoDGame.py',
            'DistributedTwoDGame',
            'enterCleanup')
        self.assertIn(
            'taskMgr.remove(self.UpdateLocalToonTask)',
            methodText)

    def test_remote_avatar_collision_masks_are_restored(self):
        onstageText = _method_text(
            'DistributedTwoDGame.py',
            'DistributedTwoDGame',
            'onstage')
        readyText = _method_text(
            'DistributedTwoDGame.py',
            'DistributedTwoDGame',
            'setGameReady')
        offstageText = _method_text(
            'DistributedTwoDGame.py',
            'DistributedTwoDGame',
            'offstage')

        self.assertIn('self.remoteToonCollideMasks = {}', onstageText)
        self.assertIn('getIntoCollideMask()', readyText)
        self.assertIn(
            'self.remoteToonCollideMasks[avId]',
            readyText)
        self.assertIn(
            'setIntoCollideMask(BitMask32.allOff())',
            readyText)
        self.assertIn(
            'setIntoCollideMask(collideMask)',
            offstageText)
        self.assertIn('self.remoteToonCollideMasks = {}', offstageText)


class RingCleanupTests(unittest.TestCase):

    def test_end_wait_and_collision_tasks_have_distinct_names(self):
        collisionTask = _class_string_constant(
            'DistributedRingGame.py',
            'DistributedRingGame',
            'COLLISION_DETECTION_TASK')
        endWaitTask = _class_string_constant(
            'DistributedRingGame.py',
            'DistributedRingGame',
            'END_GAME_WAIT_TASK')
        self.assertNotEqual(collisionTask, endWaitTask)


if __name__ == '__main__':
    unittest.main(verbosity=2)
