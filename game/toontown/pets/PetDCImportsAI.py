# This module exposes the Python classes required by the distributed-class schema for Doodle
# appearance, behavior, training, AI, and interfaces.

if hasattr(simbase, 'wantPets') and simbase.wantPets:
    from . import DistributedPetAI
