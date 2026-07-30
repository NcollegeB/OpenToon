# This module implements the client-side distributed party jukebox activity, handling network
# updates, presentation, and player interaction for party scheduling, activities, decorations, and
# services.

from toontown.parties.DistributedPartyJukeboxActivityBase import DistributedPartyJukeboxActivityBase
from toontown.parties import PartyGlobals

class DistributedPartyJukeboxActivity(DistributedPartyJukeboxActivityBase):
    notify = directNotify.newCategory('DistributedPartyJukeboxActivity')

    def __init__(self, cr):
        DistributedPartyJukeboxActivityBase.__init__(self, cr, PartyGlobals.ActivityIds.PartyJukebox, PartyGlobals.PhaseToMusicData)
