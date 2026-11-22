"""Bundled visualizer plugins and their shared host interface."""

from .api import AudioFrame, LifeExplosionPlugin, VisualizerPlugin
from .spectrum_scope import SpectrumScopePlugin

__all__ = ["AudioFrame", "LifeExplosionPlugin", "SpectrumScopePlugin", "VisualizerPlugin"]
