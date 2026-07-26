"""Focused policy and wiring tests for trolley-minigame skipping."""

import ast
from pathlib import Path
import sys
import unittest


GAME_ROOT = Path(__file__).resolve().parents[1]
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from toontown.minigame import MinigameSkipPolicy


def _load_ai_methods():
    sourcePath = (
        GAME_ROOT / 'toontown/minigame/DistributedMinigameAI.py')
    tree = ast.parse(sourcePath.read_text(encoding='utf-8'), sourcePath)
    sourceClass = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and
        node.name == 'DistributedMinigameAI')
    wanted = {
        'requestExit',
        '__sendSkipVoteStatus',
        '__grantCompletedMinigameQuestCredit',
    }
    methods = [
        node for node in sourceClass.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    if {method.name for method in methods} != wanted:
        raise AssertionError('Could not find all production skip methods')
    testClass = ast.ClassDef(
        name='MinigameAIUnderTest',
        bases=[],
        keywords=[],
        body=methods,
        decorator_list=[],
    )
    module = ast.Module(body=[testClass], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {'MinigameSkipPolicy': MinigameSkipPolicy}
    exec(compile(module, sourcePath, 'exec'), namespace)
    return namespace['MinigameAIUnderTest']


MinigameAIUnderTest = _load_ai_methods()


class _State:

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name


class _Fsm:

    def __init__(self, stateName):
        self.state = _State(stateName) if stateName else None

    def getCurrentState(self):
        return self.state


class _Notify:

    def __init__(self):
        self.messages = []

    def warning(self, message):
        self.messages.append(('warning', message))

    def debug(self, message):
        self.messages.append(('debug', message))


class _QuestManager:

    def __init__(self):
        self.calls = []

    def toonPlayedMinigame(self, toon, toons):
        self.calls.append((toon, list(toons)))


class _Air:

    def __init__(self, sender):
        self.sender = sender
        self.events = []
        self.doId2do = {}
        self.questManager = _QuestManager()

    def getAvatarIdFromSender(self):
        return self.sender

    def writeServerEvent(self, *args):
        self.events.append(args)


class _Minigame(MinigameAIUnderTest):

    def __init__(
            self,
            sender=1001,
            participants=(1001,),
            frameworkState='frameworkGame',
            gameState='play'):
        self.air = _Air(sender)
        self.avIdList = list(participants)
        self.frameworkFSM = _Fsm(frameworkState)
        self.gameFSM = _Fsm(gameState)
        self.skipVotes = set()
        self.explicitSkip = False
        self.questCreditGranted = False
        self.normalExit = 1
        self.minigameId = 6
        self.trolleyZone = 2000
        self.notify = _Notify()
        self.updates = []
        self.abortCount = 0

    def sendUpdate(self, fieldName, args):
        self.updates.append((fieldName, args))

    def setGameAbort(self):
        self.abortCount += 1
        self.normalExit = 0


class MinigameSkipPolicyTests(unittest.TestCase):

    def test_only_active_framework_game_accepts_votes(self):
        self.assertTrue(
            MinigameSkipPolicy.canRequestSkip('frameworkGame', 'play'))
        self.assertTrue(
            MinigameSkipPolicy.canRequestSkip('frameworkGame', 'swimming'))
        for frameworkState in (
                'frameworkWaitClientsJoin',
                'frameworkWaitClientsReady',
                'frameworkWaitClientsExit',
                'frameworkCleanup'):
            self.assertFalse(
                MinigameSkipPolicy.canRequestSkip(frameworkState, 'play'))
        for gameState in (None, '', 'inactive', 'off', 'cleanup'):
            self.assertFalse(
                MinigameSkipPolicy.canRequestSkip(
                    'frameworkGame', gameState))

    def test_solo_vote_is_immediately_unanimous(self):
        votes = set()
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(votes, 1001, [1001]),
            (True, True, 1, 1))
        self.assertEqual(votes, {1001})

    def test_multiplayer_requires_every_unique_participant(self):
        votes = set()
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(
                votes, 1001, [1001, 1002, 1003]),
            (False, True, 1, 3))
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(
                votes, 1002, [1001, 1002, 1003]),
            (False, True, 2, 3))
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(
                votes, 1003, [1001, 1002, 1003]),
            (True, True, 3, 3))

    def test_duplicate_vote_is_idempotent(self):
        votes = {1001}
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(
                votes, 1001, [1001, 1002]),
            (False, False, 1, 2))
        self.assertEqual(votes, {1001})

    def test_nonparticipant_vote_is_rejected(self):
        votes = set()
        self.assertEqual(
            MinigameSkipPolicy.recordSkipVote(
                votes, 9999, [1001, 1002]),
            (False, False, 0, 2))
        self.assertEqual(votes, set())

    def test_quest_credit_requires_normal_nonskipped_completion(self):
        self.assertTrue(
            MinigameSkipPolicy.shouldGrantQuestCredit(True, False, False))
        self.assertFalse(
            MinigameSkipPolicy.shouldGrantQuestCredit(False, False, False))
        self.assertFalse(
            MinigameSkipPolicy.shouldGrantQuestCredit(True, True, False))
        self.assertFalse(
            MinigameSkipPolicy.shouldGrantQuestCredit(True, False, True))


class MinigameSkipServerMethodTests(unittest.TestCase):

    def test_production_request_exit_accepts_solo_vote(self):
        game = _Minigame()
        game.requestExit()
        self.assertTrue(game.explicitSkip)
        self.assertEqual(game.skipVotes, {1001})
        self.assertEqual(game.abortCount, 1)
        self.assertIn(('setSkipVoteStatus', [1, 1]), game.updates)

    def test_production_request_exit_waits_for_unanimous_group(self):
        game = _Minigame(participants=(1001, 1002))
        game.requestExit()
        self.assertFalse(game.explicitSkip)
        self.assertEqual(game.abortCount, 0)
        game.air.sender = 1002
        game.requestExit()
        self.assertTrue(game.explicitSkip)
        self.assertEqual(game.skipVotes, {1001, 1002})
        self.assertEqual(game.abortCount, 1)
        self.assertEqual(
            [update for update in game.updates
             if update[0] == 'setSkipVoteStatus'],
            [
                ('setSkipVoteStatus', [1, 2]),
                ('setSkipVoteStatus', [2, 2]),
            ])

    def test_production_request_exit_rejects_early_and_outsider(self):
        early = _Minigame(frameworkState='frameworkWaitClientsReady')
        early.requestExit()
        self.assertEqual(early.skipVotes, set())
        self.assertEqual(early.abortCount, 0)

        outsider = _Minigame(sender=9999, participants=(1001, 1002))
        outsider.requestExit()
        self.assertEqual(outsider.skipVotes, set())
        self.assertEqual(outsider.abortCount, 0)
        self.assertTrue(outsider.air.events)

    def test_production_duplicate_vote_is_idempotent(self):
        game = _Minigame(participants=(1001, 1002))
        game.requestExit()
        game.requestExit()
        self.assertEqual(game.skipVotes, {1001})
        self.assertEqual(game.abortCount, 0)

    def test_production_quest_credit_is_completion_only_and_once(self):
        game = _Minigame(participants=(1001, 1002))
        toonOne = object()
        toonTwo = object()
        game.air.doId2do = {1001: toonOne, 1002: toonTwo}
        game._MinigameAIUnderTest__grantCompletedMinigameQuestCredit()
        game._MinigameAIUnderTest__grantCompletedMinigameQuestCredit()
        self.assertEqual(len(game.air.questManager.calls), 2)
        self.assertTrue(game.questCreditGranted)
        for toon, toons in game.air.questManager.calls:
            self.assertIn(toon, (toonOne, toonTwo))
            self.assertEqual(toons, [toonOne, toonTwo])

        skipped = _Minigame()
        skipped.explicitSkip = True
        skipped.air.doId2do = {1001: object()}
        skipped._MinigameAIUnderTest__grantCompletedMinigameQuestCredit()
        self.assertEqual(skipped.air.questManager.calls, [])


class MinigameSkipWiringTests(unittest.TestCase):

    def _read(self, relativePath):
        return (GAME_ROOT / relativePath).read_text(encoding='utf-8')

    def test_all_changed_sources_parse(self):
        paths = (
            'toontown/minigame/MinigameSkipPolicy.py',
            'toontown/minigame/DistributedMinigame.py',
            'toontown/minigame/DistributedMinigameAI.py',
            'toontown/minigame/MinigameCreatorAI.py',
            'toontown/minigame/DistributedTwoDGameAI.py',
            'toontown/minigame/DistributedMazeGameAI.py',
            'toontown/minigame/DistributedDivingGameAI.py',
        )
        for relativePath in paths:
            source = self._read(relativePath)
            ast.parse(source, filename=relativePath)

    def test_network_vote_and_confirmation_are_wired(self):
        dcSource = self._read('etc/toon.dc')
        clientSource = self._read(
            'toontown/minigame/DistributedMinigame.py')
        aiSource = self._read(
            'toontown/minigame/DistributedMinigameAI.py')
        self.assertIn(
            'setSkipVoteStatus(uint8, uint8) broadcast;', dcSource)
        self.assertIn('MinigameSkipConfirm', clientSource)
        self.assertIn('recordSkipVote', aiSource)
        self.assertIn("'minigame_skipped'", aiSource)
        self.assertIn('score = 0', aiSource)

    def test_dc_schema_parses_after_vote_field_addition(self):
        from panda3d.direct import DCFile
        from panda3d.core import Filename
        dcFile = DCFile()
        dcPath = Filename.fromOsSpecific(
            str(GAME_ROOT / 'etc/toon.dc'))
        self.assertTrue(dcFile.read(dcPath))
        self.assertGreater(dcFile.getNumClasses(), 0)

    def test_quest_credit_moved_out_of_creation(self):
        creatorSource = self._read(
            'toontown/minigame/MinigameCreatorAI.py')
        aiSource = self._read(
            'toontown/minigame/DistributedMinigameAI.py')
        self.assertNotIn('toonPlayedMinigame(', creatorSource)
        self.assertIn('toonPlayedMinigame(toon, toons)', aiSource)
        self.assertIn('shouldGrantQuestCredit', aiSource)

    def test_quest_credit_is_granted_before_the_client_exit_barrier(self):
        aiSource = self._read(
            'toontown/minigame/DistributedMinigameAI.py')
        gameOverStart = aiSource.index('    def gameOver(self):')
        grantIndex = aiSource.index(
            'self.__grantCompletedMinigameQuestCredit()', gameOverStart)
        exitBarrierIndex = aiSource.index(
            "self.frameworkFSM.request('frameworkWaitClientsExit')",
            gameOverStart)
        self.assertLess(grantIndex, exitBarrierIndex)

    def test_cleanup_guards_cover_known_early_abort_fields(self):
        twoDSource = self._read(
            'toontown/minigame/DistributedTwoDGameAI.py')
        mazeSource = self._read(
            'toontown/minigame/DistributedMazeGameAI.py')
        divingSource = self._read(
            'toontown/minigame/DistributedDivingGameAI.py')
        self.assertIn("hasattr(self, 'doneBarrier')", twoDSource)
        self.assertIn("hasattr(self, 'takenTable')", mazeSource)
        self.assertIn("getattr(self, 'spawnings', [])", divingSource)


if __name__ == '__main__':
    unittest.main(verbosity=2)
