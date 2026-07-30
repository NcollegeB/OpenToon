# This module implements the client-side distributed party winter trampoline activity, handling
# network updates, presentation, and player interaction for party scheduling, activities,
# decorations, and services.

from toontown.parties.DistributedPartyTrampolineActivity import DistributedPartyTrampolineActivity

class DistributedPartyWinterTrampolineActivity(DistributedPartyTrampolineActivity):

    def __init__(self, cr, doJellyBeans = True, doTricks = False, texture = None):
        DistributedPartyTrampolineActivity.__init__(self, cr, doJellyBeans, doTricks, 'phase_13/maps/tt_t_ara_pty_trampolineWinter.png')
