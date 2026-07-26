"""Focused regression tests for target and photo minigame cleanup."""

import ast
from pathlib import Path
import unittest


GAME_ROOT = Path(__file__).resolve().parents[1]


def _class_node(relativePath, className):
    sourcePath = GAME_ROOT / relativePath
    tree = ast.parse(sourcePath.read_text(encoding='utf-8'), sourcePath)
    return sourcePath, next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == className)


def _load_methods(relativePath, className, methodNames, namespace=None):
    sourcePath, sourceClass = _class_node(relativePath, className)
    methods = [
        node for node in sourceClass.body
        if isinstance(node, ast.FunctionDef) and node.name in methodNames
    ]
    if {method.name for method in methods} != set(methodNames):
        raise AssertionError('Could not find all cleanup methods')
    testClass = ast.ClassDef(
        name=className,
        bases=[],
        keywords=[],
        body=methods,
        decorator_list=[],
    )
    module = ast.Module(body=[testClass], type_ignores=[])
    ast.fix_missing_locations(module)
    moduleNamespace = {} if namespace is None else dict(namespace)
    exec(compile(module, sourcePath, 'exec'), moduleNamespace)
    return moduleNamespace[className]


def _called_methods(relativePath, className, methodName):
    unusedPath, sourceClass = _class_node(relativePath, className)
    sourceMethod = next(
        node for node in sourceClass.body
        if isinstance(node, ast.FunctionDef) and node.name == methodName)
    return {
        node.func.attr for node in ast.walk(sourceMethod)
        if isinstance(node, ast.Call) and
        isinstance(node.func, ast.Attribute)
    }


class _TaskManager:

    def __init__(self):
        self.removed = []
        self.scheduled = []

    def remove(self, taskName):
        self.removed.append(taskName)

    def doMethodLater(
            self, delay, callback, taskName, extraArgs=None, **unused):
        self.scheduled.append({
            'delay': delay,
            'callback': callback,
            'taskName': taskName,
            'extraArgs': list(extraArgs or ()),
        })


class _Interval:

    def __init__(self):
        self.pauseCount = 0

    def pause(self):
        self.pauseCount += 1


class _RubberBand:

    def __init__(self):
        self.deleteCount = 0

    def delete(self):
        self.deleteCount += 1


class _Barrier:

    def __init__(self):
        self.cleanupCount = 0

    def cleanup(self):
        self.cleanupCount += 1


class _State:

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name


class _Fsm:

    def __init__(self, stateName):
        self.state = _State(stateName)
        self.requests = []

    def getCurrentState(self):
        return self.state

    def request(self, stateName):
        self.requests.append(stateName)


class _Buffer:

    def __init__(self):
        self.activeUpdates = []

    def setActive(self, active):
        self.activeUpdates.append(active)


class _Sound:

    def __init__(self):
        self.stopCount = 0

    def stop(self):
        self.stopCount += 1


class _Task:
    done = 'done'


class TargetClientCleanupTests(unittest.TestCase):

    def setUp(self):
        self.taskMgr = _TaskManager()
        self.targetClass = _load_methods(
            'toontown/minigame/DistributedTargetGame.py',
            'DistributedTargetGame',
            {
                '_deleteRubberBands',
                '_stopRuntimeInterval',
                '_cleanupRuntime',
            },
            {'taskMgr': self.taskMgr},
        )

    def test_runtime_cleanup_cancels_every_late_task_and_interval_once(self):
        game = self.targetClass()
        taskConstants = {
            'UPDATE_ENVIRON_TASK': 'environment',
            'UPDATE_LOCALTOON_TASK': 'local-toon',
            'UPDATE_SHADOWS_TASK': 'shadows',
            'COLLISION_DETECTION_TASK': 'collisions',
            'END_GAME_WAIT_TASK': 'end-wait',
            'UPDATE_POWERBAR_TASK': 'power',
            'GAME_DONE_TASK': 'game-done',
            'UPDATE_COUNTDOWN_TASK': 'countdown',
            'TOONSTRETCHTASK': 'stretch',
        }
        for name, value in taskConstants.items():
            setattr(game, name, value)
        intervals = {
            name: _Interval() for name in (
                'cameraWork',
                'flyToFallCameraTrack',
                'scoreCameraTrack',
                'localTrack')
        }
        for name, interval in intervals.items():
            setattr(game, name, interval)

        game._cleanupRuntime()
        game._cleanupRuntime()

        self.assertEqual(
            set(self.taskMgr.removed), set(taskConstants.values()))
        for name, interval in intervals.items():
            self.assertEqual(interval.pauseCount, 1)
            self.assertIsNone(getattr(game, name))

    def test_rubber_band_cleanup_clears_owned_list_idempotently(self):
        game = self.targetClass()
        bands = [_RubberBand(), _RubberBand()]
        game.rubberBands = bands

        game._deleteRubberBands()
        game._deleteRubberBands()

        self.assertEqual(game.rubberBands, [])
        self.assertEqual([band.deleteCount for band in bands], [1, 1])

    def test_offstage_uses_owned_rubber_band_cleanup(self):
        calls = _called_methods(
            'toontown/minigame/DistributedTargetGame.py',
            'DistributedTargetGame',
            'offstage')
        self.assertIn('_deleteRubberBands', calls)
        self.assertIn('_cleanupRuntime', calls)

    def test_end_wait_and_collision_tasks_have_distinct_names(self):
        unusedPath, sourceClass = _class_node(
            'toontown/minigame/DistributedTargetGame.py',
            'DistributedTargetGame')
        constants = {}
        for node in sourceClass.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if (
                    isinstance(target, ast.Name) and
                    target.id in (
                        'COLLISION_DETECTION_TASK',
                        'END_GAME_WAIT_TASK')):
                constants[target.id] = ast.literal_eval(node.value)
        self.assertNotEqual(
            constants['COLLISION_DETECTION_TASK'],
            constants['END_GAME_WAIT_TASK'])


class TargetServerCleanupTests(unittest.TestCase):

    def setUp(self):
        self.taskMgr = _TaskManager()
        self.serverClass = _load_methods(
            'toontown/minigame/DistributedTargetGameAI.py',
            'DistributedTargetGameAI',
            {
                '_removeRoundResetTask',
                '_cleanupBarrierScore',
                'gotoFly',
                'allAvatarsScore',
            },
            {'taskMgr': self.taskMgr},
        )

    def test_barrier_and_round_reset_cleanup_are_idempotent(self):
        game = self.serverClass()
        barrier = _Barrier()
        game.barrierScore = barrier
        game.taskName = lambda name: 'target-' + name

        game._cleanupBarrierScore()
        game._cleanupBarrierScore()
        game._removeRoundResetTask()
        game._removeRoundResetTask()

        self.assertEqual(barrier.cleanupCount, 1)
        self.assertIsNone(game.barrierScore)
        self.assertEqual(
            self.taskMgr.removed,
            ['target-roundReset', 'target-roundReset'])

    def test_late_round_reset_and_barrier_callbacks_are_ignored(self):
        game = self.serverClass()
        game.gameFSM = _Fsm('inactive')
        fsm = game.gameFSM
        game.round = 2

        game.gotoFly()
        game.allAvatarsScore()
        del game.gameFSM
        game.gotoFly()
        game.allAvatarsScore()

        self.assertEqual(fsm.requests, [])
        self.assertEqual(game.round, 2)

    def test_server_cleanup_wires_both_barrier_and_task_shutdown(self):
        calls = _called_methods(
            'toontown/minigame/DistributedTargetGameAI.py',
            'DistributedTargetGameAI',
            'enterCleanup')
        self.assertIn('_cleanupBarrierScore', calls)
        self.assertIn('_removeRoundResetTask', calls)

    def test_exit_fly_cleans_the_score_barrier(self):
        calls = _called_methods(
            'toontown/minigame/DistributedTargetGameAI.py',
            'DistributedTargetGameAI',
            'exitFly')
        self.assertIn('_cleanupBarrierScore', calls)


class PhotoCleanupTests(unittest.TestCase):

    def setUp(self):
        self.taskMgr = _TaskManager()
        self.photoClass = _load_methods(
            'toontown/minigame/DistributedPhotoGame.py',
            'DistributedPhotoGame',
            {
                '_scheduleCaptureDeactivate',
                '_deactivateCaptureBuffer',
                '_cancelCaptureTasks',
                '_pauseRuntimeInterval',
                '_cleanupRuntime',
            },
            {'taskMgr': self.taskMgr, 'Task': _Task},
        )

    def _newPhotoGame(self):
        game = self.photoClass()
        game.captureTaskSerial = 0
        game.captureTaskNames = set()
        game.captureTaskByBuffer = {}
        game.textureBuffers = []
        game.taskName = lambda name: 'photo-' + name
        return game

    def test_capture_tasks_are_unique_and_individually_retired(self):
        game = self._newPhotoGame()
        buffer = _Buffer()
        game.textureBuffers = [buffer]

        game._scheduleCaptureDeactivate(buffer)
        game._scheduleCaptureDeactivate(buffer)

        names = [
            scheduled['taskName'] for scheduled in self.taskMgr.scheduled]
        self.assertEqual(len(names), 2)
        self.assertEqual(len(set(names)), 2)
        self.assertIn(names[0], self.taskMgr.removed)
        self.assertNotIn(names[0], game.captureTaskNames)
        self.assertIn(names[1], game.captureTaskNames)
        first = self.taskMgr.scheduled[0]
        result = first['callback'](*first['extraArgs'])
        self.assertEqual(result, _Task.done)
        self.assertEqual(buffer.activeUpdates, [])
        self.assertNotIn(names[0], game.captureTaskNames)
        self.assertIn(names[1], game.captureTaskNames)
        second = self.taskMgr.scheduled[1]
        second['callback'](*second['extraArgs'])
        self.assertEqual(buffer.activeUpdates, [0])
        self.assertNotIn(names[1], game.captureTaskNames)

    def test_capture_tasks_cancel_before_buffers_are_removed(self):
        game = self._newPhotoGame()
        buffer = _Buffer()
        game.textureBuffers = [buffer]
        game._scheduleCaptureDeactivate(buffer)
        scheduled = self.taskMgr.scheduled[0]

        game._cancelCaptureTasks()
        game.textureBuffers = []
        scheduled['callback'](*scheduled['extraArgs'])

        self.assertEqual(game.captureTaskNames, set())
        self.assertEqual(
            self.taskMgr.removed, [scheduled['taskName']])
        self.assertEqual(buffer.activeUpdates, [])

    def test_runtime_cleanup_stops_tracks_and_pending_capture(self):
        game = self._newPhotoGame()
        game.VIEWFINDER_TASK_NAME = 'viewfinder'
        game.LOCAL_PHOTO_MOVE_TASK = 'photo-move'
        game.INTRO_TASK_NAME = 'intro'
        game.INTRO_TASK_NAME_CAMERA_LERP = 'intro-camera'
        game.FIRE_KEY = 'fire'
        game.UP_KEY = 'up'
        game.DOWN_KEY = 'down'
        game.LEFT_KEY = 'left'
        game.RIGHT_KEY = 'right'
        game.avIdList = [1001, 1002]
        game.ignored = []
        game.ignore = game.ignored.append
        game.photoMoving = 1
        game.sndPhotoMove = _Sound()
        cameraTrack = _Interval()
        introSequence = _Interval()
        subjectTrack = _Interval()
        game.cameraTrack = cameraTrack
        game.introSequence = introSequence
        game.subjectTracks = {'subject': (subjectTrack, ())}
        game.captureTaskNames = {'capture-one'}

        game._cleanupRuntime()
        game._cleanupRuntime()

        self.assertIsNone(game.cameraTrack)
        self.assertIsNone(game.introSequence)
        self.assertEqual(game.subjectTracks, {})
        self.assertEqual(cameraTrack.pauseCount, 1)
        self.assertEqual(introSequence.pauseCount, 1)
        self.assertEqual(subjectTrack.pauseCount, 1)
        self.assertEqual(game.sndPhotoMove.stopCount, 1)
        self.assertEqual(game.captureTaskNames, set())
        self.assertIn('capture-one', self.taskMgr.removed)

    def test_photo_cleanup_uses_central_runtime_shutdown(self):
        calls = _called_methods(
            'toontown/minigame/DistributedPhotoGame.py',
            'DistributedPhotoGame',
            'enterCleanup')
        self.assertIn('_cleanupRuntime', calls)


if __name__ == '__main__':
    unittest.main()
