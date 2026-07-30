# This module imports the ToonBase application class, constructs the process-wide client base
# instance, and exports that singleton for legacy wildcard imports.

__all__ = ['base']

from .ToonBase import ToonBase

base = ToonBase()
