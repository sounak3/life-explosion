"""Common interface shared by bundled visualization renderers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class AudioFrame:
    """Latest audio data supplied by the host to a visualization plugin."""

    level: float
    bass: float
    treble: float
    beat_pulse: float
    spectrum: tuple[float, ...] = ()
    pcm: Any = None
    sample_rate: int = 0


class VisualizerPlugin(Protocol):
    """Renderer contract for a host-composited visualization plugin.

    A plugin owns only its visualization state. The host owns audio output,
    preset/plugin selection, crossfades, display mode, and user input.
    Renderers receive a per-frame audio snapshot and return a pygame-compatible
    surface at the requested dimensions.
    Native engines can adapt their output into that surface while retaining
    their own native resources behind activate/deactivate.
    """

    plugin_id: str
    name: str

    def activate(self) -> None: ...

    def deactivate(self) -> None: ...

    def render(self, width: int, height: int, dt: float, audio: AudioFrame) -> Any: ...


class LifeExplosionPlugin:
    """Adapter that exposes the existing Life Explosion renderer as a plugin."""

    plugin_id = "life-explosion"
    name = "Life Explosion"

    def __init__(self, render_callback: Callable[[int, int, float, AudioFrame], Any]):
        self._render_callback = render_callback

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def render(self, width: int, height: int, dt: float, audio: AudioFrame) -> Any:
        return self._render_callback(width, height, dt, audio)
