# This module exposes the Python classes required by the distributed-class schema for Doodle
# appearance, behavior, training, AI, and interfaces.

if hasattr(base, 'wantPets') and base.wantPets:
    from . import DistributedPet
