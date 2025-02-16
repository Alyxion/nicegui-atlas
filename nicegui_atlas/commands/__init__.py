"""Command plugins for NiceGUI Atlas."""

from .base import registry, CommandPlugin
from . import info, index, build, qinfo, backup

__all__ = ['registry', 'CommandPlugin']
