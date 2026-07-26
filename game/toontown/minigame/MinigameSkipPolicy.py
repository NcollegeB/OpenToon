"""Pure policy helpers for safe, unanimous trolley-minigame skipping."""


INACTIVE_GAME_STATES = frozenset(('inactive', 'off', 'cleanup'))


def canRequestSkip(frameworkStateName, gameStateName):
    """Return whether a skip vote may be accepted in the current lifecycle."""
    return (
        frameworkStateName == 'frameworkGame' and
        bool(gameStateName) and
        gameStateName not in INACTIVE_GAME_STATES
    )


def recordSkipVote(votes, avId, participants):
    """Record one participant vote and return status without side effects.

    The returned tuple is ``(accepted, added, voteCount, requiredCount)``.
    ``votes`` is mutated only for a valid, new participant vote.
    """
    participantSet = set(participants)
    required = len(participantSet)
    if avId not in participantSet or required == 0:
        return False, False, len(votes), required
    if avId in votes:
        return len(votes) >= required, False, len(votes), required
    votes.add(avId)
    return len(votes) >= required, True, len(votes), required


def shouldGrantQuestCredit(normalExit, explicitSkip, alreadyGranted):
    """Return whether this cleanup represents one completed minigame."""
    return bool(normalExit and not explicitSkip and not alreadyGranted)
