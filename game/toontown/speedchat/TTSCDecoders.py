# This module re-exports the ToonTask and Resistance SpeedChat message decoders through one shared
# import point.

from .TTSCToontaskTerminal import decodeTTSCToontaskMsg
from .TTSCResistanceTerminal import decodeTTSCResistanceMsg
