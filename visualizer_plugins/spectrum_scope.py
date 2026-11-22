"""Built-in spectrum-scope visualizer plugin using host-provided audio bands."""
from __future__ import annotations

import math

import pygame

from .api import AudioFrame


class SpectrumScopePlugin:
    plugin_id = "spectrum-scope"
    name = "Spectrum Scope"
    BACKGROUND = (4, 5, 14)

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def render(self, width: int, height: int, dt: float, audio: AudioFrame) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill(self.BACKGROUND)
        bands = audio.spectrum or (0.0,) * 32
        count = len(bands)
        if not count:
            return surface

        margin = max(24, width // 18)
        span = max(1, width - margin * 2)
        slot = span / count
        center_y = height // 2
        max_half_height = max(8, int(height * 0.38))
        pulse = min(1.0, max(0.0, audio.beat_pulse))
        for index, value in enumerate(bands):
            # A mild curve keeps quieter bins visible without flattening peaks.
            energy = min(1.0, math.sqrt(max(0.0, float(value))))
            bar_height = max(2, int(max_half_height * min(1.0, energy * 1.45 + pulse * 0.14)))
            x = margin + int(index * slot)
            bar_width = max(2, int(slot * 0.68))
            hue = index / max(1, count - 1)
            color = (
                min(255, int(60 + 170 * hue + 30 * pulse)),
                min(255, int(110 + 110 * (1.0 - abs(hue - 0.5) * 2) + 45 * pulse)),
                min(255, int(230 - 150 * hue + 25 * pulse)),
            )
            pygame.draw.rect(surface, color,
                             (x, center_y - bar_height, bar_width, bar_height * 2),
                             border_radius=max(1, bar_width // 3))
        pygame.draw.line(surface, (36, 46, 66), (margin, center_y),
                         (width - margin, center_y), 1)
        return surface
