# This module implements the client-side distributed party winter Cog activity, handling network
# updates, presentation, and player interaction for party scheduling, activities, decorations, and
# services.

from toontown.parties.DistributedPartyCogActivity import DistributedPartyCogActivity

class DistributedPartyWinterCogActivity(DistributedPartyCogActivity):

    def __init__(self, cr):
        DistributedPartyCogActivity.__init__(self, cr, 'phase_13/models/parties/tt_m_ara_pty_cogPieArenaWinter')
