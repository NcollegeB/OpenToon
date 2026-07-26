"""Launch one repeatable live-test client and optionally board the trolley."""

import argparse
import os
import sys


GAME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if GAME_ROOT not in sys.path:
    sys.path.insert(0, GAME_ROOT)

from panda3d.core import loadPrcFile, loadPrcFileData, WindowProperties


def _parseArguments():
    parser = argparse.ArgumentParser(
        description=(
            'Launch a uniquely named client for live trolley-minigame tests.'))
    parser.add_argument('--client-label', default='1')
    parser.add_argument('--title', default='Open Town Live Test')
    parser.add_argument('--minigame', default='')
    parser.add_argument('--slot', type=int, default=0)
    parser.add_argument('--width', type=int, default=960)
    parser.add_argument('--height', type=int, default=540)
    parser.add_argument('--x', type=int, default=0)
    parser.add_argument('--y', type=int, default=0)
    parser.add_argument('--log-file', default='')
    parser.add_argument(
        '--no-auto-board',
        action='store_true',
        help='Enter the playground without requesting a trolley seat.')
    return parser.parse_args()


def _redirectOutput(options):
    if not options.log_file:
        return

    logPath = os.path.abspath(options.log_file)
    logDirectory = os.path.dirname(logPath)
    if logDirectory and not os.path.isdir(logDirectory):
        os.makedirs(logDirectory)
    logStream = open(logPath, 'w', buffering=1, encoding='utf-8')
    sys.stdout = logStream
    sys.stderr = logStream
    sys.__stdout__ = logStream
    sys.__stderr__ = logStream


def _loadClientConfig(options):
    loadPrcFile('etc/Configrc.prc')
    loadPrcFileData(
        'live-minigame-client',
        '\n'.join((
            'auto-avatar-choice %s' % options.slot,
            'window-title %s' % options.title,
            'win-size %s %s' % (options.width, options.height),
            'win-origin %s %s' % (options.x, options.y),
            'fullscreen #f',
        )))


def _applyWindowProperties(options):
    properties = WindowProperties()
    properties.setSize(options.width, options.height)
    properties.setOrigin(options.x, options.y)
    properties.setFullscreen(False)
    base.win.requestProperties(properties)


def _findTrolley():
    from toontown.safezone.DistributedTrolley import DistributedTrolley

    localZone = getattr(base.localAvatar, 'zoneId', None)
    for distributedObject in base.cr.doId2do.values():
        if (
                isinstance(distributedObject, DistributedTrolley) and
                getattr(distributedObject, 'zoneId', None) == localZone):
            return distributedObject
    return None


def _currentStateName(fsm):
    state = fsm.getCurrentState() if fsm else None
    return state.getName() if state else None


def _launch(options):
    from toontown.launcher.QuickLauncher import QuickLauncher

    class LiveMinigameLauncher(QuickLauncher):

        def __init__(self):
            self.liveOptions = options
            self.liveRequestSent = False
            self.liveBoardSent = False
            QuickLauncher.__init__(self)

        def startGame(self):
            QuickLauncher.startGame(self)
            from direct.task.TaskManagerGlobal import taskMgr

            _applyWindowProperties(self.liveOptions)
            taskMgr.doMethodLater(
                0.5,
                self.__prepareLiveRun,
                'prepare-live-minigame-%s' %
                self.liveOptions.client_label)

        def __prepareLiveRun(self, task):
            from direct.task.Task import Task

            if (
                    not hasattr(base, 'localAvatar') or
                    not getattr(base, 'cr', None) or
                    base.localAvatar.getTransitioning()):
                return Task.again

            place = base.cr.playGame.getPlace()
            if not place:
                return Task.again

            placeState = _currentStateName(place.fsm)
            if placeState == 'popup':
                from direct.showbase.MessengerGlobal import messenger
                messenger.send('escape')
                return Task.again

            if placeState not in ('walk', 'trolley'):
                return Task.again

            if self.liveOptions.minigame and not self.liveRequestSent:
                magicWordManager = getattr(
                    base.cr, 'magicWordManager', None)
                if not magicWordManager:
                    return Task.again
                magicWordManager.checkMagicWord(
                    '~mg request %s' % self.liveOptions.minigame)
                self.liveRequestSent = True
                print(
                    '[live-client %s] requested %s' %
                    (self.liveOptions.client_label,
                     self.liveOptions.minigame))

            if self.liveOptions.no_auto_board:
                return Task.done

            trolley = _findTrolley()
            if (
                    not trolley or
                    _currentStateName(trolley.fsm) not in (
                        'waitEmpty', 'waitCountdown')):
                return Task.again

            if not hasattr(place, 'trolley'):
                place.detectedTrolleyCollision()
                return Task.again

            if not self.liveBoardSent:
                trolley.sendUpdate('requestBoard', [])
                self.liveBoardSent = True
                print(
                    '[live-client %s] requested trolley seat' %
                    self.liveOptions.client_label)
            return Task.done

    LiveMinigameLauncher()


def main():
    options = _parseArguments()
    if not os.environ.get('LOGIN_TOKEN'):
        raise SystemExit(
            'LOGIN_TOKEN must identify a distinct local test account.')
    os.environ.setdefault('GAME_SERVER', '127.0.0.1')
    _redirectOutput(options)
    _loadClientConfig(options)
    _launch(options)


if __name__ == '__main__':
    main()
