"""Command plugins for NiceGUI Atlas."""

from .base import registry, CommandPlugin
from . import info, index, verify, build

__all__ = ['registry', 'CommandPlugin']
