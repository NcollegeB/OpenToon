# This module manages the client location lifecycle, state transitions, and interactions for
# Minnie's Melodyland street within streets, town loading, place state, and street battles.

from . import Street

class MMStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Street.Street.load(self)

    def unload(self):
        Street.Street.unload(self)
