#!/usr/bin/env python3
"""A small audio-reactive particle visualizer inspired by Life Explosion."""
from __future__ import annotations

import math
import random
import re
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

import numpy as np
import pygame
import soundfile as sf

from visualizer_plugins import AudioFrame, LifeExplosionPlugin, SpectrumScopePlugin

PRESETS = ["Helix", "Solar Bloom", "Vortex", "Nebula", "Shockwave"]
BG = (4, 5, 14)
SILENT_TEST_MODE = False
PRESET_FADE_SECONDS = 1.0
TILE_MIN_EXTENTS = {
    # Minimum measured width/height percentages across five silent runs.
    "big mac": (23, 44),
    "vagary": (31, 51),
    "lambent": (32, 62),
    "kinematic": (35, 60),
    "imaginary": (39, 70),
    "trace": (47, 81),
    "zombie": (36, 69),
    "felicity": (71, 99),
    "massaraksh": (68, 100),
    "peachy by ensi kay": (92, 100),
}
@dataclass(frozen=True)
class LifeExplosionPreset:
    name: str
    values: tuple[int, ...] | None = None


def load_presets():
    """Load the original preset names and numeric controls when available."""
    directory = Path(__file__).resolve().parent / "assets" / "lifeexplosion_original" / "Group1"
    presets = []
    for path in sorted(directory.glob("*.xpl"), key=lambda item: item.name.casefold()):
        lines = path.read_text(encoding="cp1252", errors="replace").splitlines()
        if not lines or lines[0].strip() != "Life Explosion preset.Version 1.0":
            continue
        record = next((line.strip() for line in lines[1:] if line.startswith("<")), "")
        match = re.fullmatch(r"<([^>]*)>([0-9]+(?:\.[0-9]+){14})\.", record)
        if not match:
            continue
        values = tuple(int(value) for value in match.group(2).split("."))
        presets.append(LifeExplosionPreset(match.group(1), values))
    return presets or [LifeExplosionPreset(name) for name in PRESETS]


class AudioEngine:
    """Plays decoded audio through SDL and analyzes the playback position."""
    def __init__(self):
        self.data = None
        self.rate = 44100
        self.position = 0
        self.playing = False
        self.muted = False
        self.channel = None
        self.sound = None
        self.started_at = 0.0
        self.level = self.bass = self.treble = 0.0
        self.beat_count = 0
        self.last_beat_time = 0.0
        self.prev_spectrum = None
        self.flux_history = deque(maxlen=32)
        self.file_name = "No track selected"
        self.spectrum_bands = np.zeros(32, dtype=np.float32)
        self.latest_pcm = None

    def load(self, filename: str):
        samples, rate = sf.read(filename, dtype="float32", always_2d=True)
        if samples.shape[1] > 2:
            samples = samples[:, :2]
        pygame.mixer.quit()
        pygame.mixer.init(frequency=int(rate), size=-16,
                          channels=samples.shape[1], buffer=1024)
        pcm = np.clip(samples * 32767.0, -32768, 32767).astype(np.int16)
        self.sound = pygame.sndarray.make_sound(pcm)
        self.data = samples
        self.rate = int(rate)
        self.position = 0
        self.level = self.bass = self.treble = 0.0
        self.beat_count = 0
        self.prev_spectrum = None
        self.flux_history.clear()
        self.spectrum_bands.fill(0.0)
        self.latest_pcm = None
        self.file_name = Path(filename).name
        self.channel = self.sound.play()
        if self.channel is None:
            raise RuntimeError("The audio mixer could not start playback.")
        self.started_at = time.monotonic()
        self.channel.set_volume(0.0 if self.muted else 1.0)
        self.playing = True

    def update(self):
        if self.data is None:
            return self.level, self.bass, self.treble, self.beat_count
        if self.playing:
            if self.channel is None or not self.channel.get_busy():
                self.playing = False
            else:
                self.position = min(len(self.data), int((time.monotonic() - self.started_at) * self.rate))
        end = self.position
        start = max(0, end - 2048)
        chunk = self.data[start:end]
        if len(chunk) < 64:
            return self.level, self.bass, self.treble, self.beat_count
        mono = chunk.mean(axis=1)
        rms = float(np.sqrt(np.mean(mono * mono)))
        self.latest_pcm = chunk.astype(np.float32, copy=True)
        spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
        freqs = np.fft.rfftfreq(len(mono), 1.0 / self.rate)
        edges = np.geomspace(35.0, max(36.0, min(self.rate / 2, 16000.0)), 33)
        bands = []
        for low, high in zip(edges[:-1], edges[1:]):
            values = spectrum[(freqs >= low) & (freqs < high)]
            bands.append(float(values.mean()) if len(values) else 0.0)
        band_scale = float(spectrum.mean()) * 3.0 + 1e-7
        self.spectrum_bands = np.clip(np.sqrt(np.asarray(bands) / band_scale), 0.0, 1.0)
        bass = float(spectrum[(freqs >= 35) & (freqs < 180)].mean()) if len(spectrum) else 0
        treble = float(spectrum[(freqs >= 1800) & (freqs < 8000)].mean()) if len(spectrum) else 0
        total = float(spectrum.mean()) + 1e-7
        self.bass = min(1.0, bass / (total * 4.0))
        self.treble = min(1.0, treble / (total * 4.0))
        flux = 0.0
        if self.prev_spectrum is not None and len(spectrum) == len(self.prev_spectrum):
            flux = float(np.maximum(0, spectrum - self.prev_spectrum).mean())
        baseline = (sum(self.flux_history) / len(self.flux_history)) if self.flux_history else 0
        now = time.monotonic()
        if (len(self.flux_history) >= 5 and flux > max(0.012, baseline * 1.55)
                and now - self.last_beat_time > 0.24):
            self.beat_count += 1
            self.last_beat_time = now
        self.flux_history.append(flux)
        self.prev_spectrum = spectrum
        self.level = min(1.0, max(self.level * 0.78, rms * 4.0))
        return self.level, self.bass, self.treble, self.beat_count

    def toggle_mute(self):
        self.muted = not self.muted
        if self.channel is not None:
            self.channel.set_volume(0.0 if self.muted else 1.0)

    def toggle(self):
        if self.channel is None or self.data is None:
            return
        if self.playing:
            self.position = min(len(self.data), int((time.monotonic() - self.started_at) * self.rate))
            self.channel.pause()
            self.playing = False
        else:
            self.channel.unpause()
            self.started_at = time.monotonic() - self.position / self.rate
            self.playing = True

    def stop(self):
        self.playing = False
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
        self.sound = None
        self.data = None
        pygame.mixer.quit()


class LifeExplosionField:
    """Approximate the recovered bitmap particle engine, ticked at 100 Hz."""
    PARTICLE_COUNT = 2800  # recovered defaults: 400 particles in each of 7 groups
    GROUP_SIZE = 400
    TICK_SECONDS = 0.01  # the original TTimer interval is 10 ms

    def __init__(self):
        self.size = None
        self.pixels = None
        self.surface = None
        self.elapsed = 0.0
        self.reset_pending = True
        self.cycle_count = 0

    def reset(self, size, preset):
        self.size = size
        self.pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        self.surface = None
        self.elapsed = 0.0
        self.reset_pending = False

        values = preset.values or (128, 120, 128, 120, 128, 120,
                                   5, 11, 5, 20, 200, 59, 2, 180, 180)
        count = self.PARTICLE_COUNT
        index = np.arange(count, dtype=np.float32)
        self.x = np.empty(count, dtype=np.float32)
        self.y = np.empty(count, dtype=np.float32)
        self.vx = np.empty(count, dtype=np.float32)
        self.vy = np.empty(count, dtype=np.float32)
        self.rgb = np.zeros((count, 3), dtype=np.int16)
        self.delay = np.zeros(count, dtype=np.int16)

        # Reset recentres the source in the half-size DIB.
        cx, cy = size[0] // 2, size[1] // 2
        radius_pos, radius_width = values[6], values[7]
        speed_pos, speed_width = values[8], values[9]
        radius = radius_pos + np.random.randint(0, max(1, radius_width + 1), count)
        if speed_width > 5:
            radius = radius + np.rint(index / speed_width)
            angle_x = index * math.pi / max(1, values[13])
            angle_y = index * math.pi / max(1, values[14])
        else:
            # The original converts integer degrees to radians: degree * pi / 180.
            angle = np.random.randint(0, 360, count) * (math.pi / 180.0)
            angle_x = angle_y = angle
        self.x[:] = cx + radius * np.sin(angle_x)
        self.y[:] = cy + radius * np.cos(angle_y)

        # The original derives each component from an independent random angle,
        # then scales it by speed and a random 0..99 percentage.
        angle_x = np.random.randint(0, 360, count) * (math.pi / 180.0)
        angle_y = np.random.randint(0, 360, count) * (math.pi / 180.0)
        magnitude_x = np.random.randint(0, 100, count) * 0.01 * speed_pos
        magnitude_y = np.random.randint(0, 100, count) * 0.01 * speed_pos
        self.vx[:] = np.sin(angle_x) * magnitude_x
        self.vy[:] = np.cos(angle_y) * magnitude_y

        # The executable refreshes a shared random color every 400 particles.
        for first in range(0, count, self.GROUP_SIZE):
            color = [values[0] + random.randrange(max(1, values[1])),
                     values[2] + random.randrange(max(1, values[3])),
                     values[4] + random.randrange(max(1, values[5]))]
            self.rgb[first:first + self.GROUP_SIZE] = color
        self.rgb[-150:] = 0  # the original reserves the last 150 slots as dark
        life_position = max(1, values[10])
        life_width = max(1, values[11])
        # Particles activate in index order, staggered by the preset's life
        # interval. The last 150 are deliberately delayed and remain dark.
        self.delay[:] = np.arange(count, dtype=np.int32) // life_width
        self.delay[-150:] += 10
        self.life_position = life_position
        self.life_remaining = self.life_position
        self.shade = values[12]
        self.speed_gain = 1.0

    @staticmethod
    def _blur_four_neighbors(image):
        """Match the original four-neighbor, quarter-sum bitmap filter."""
        out = np.zeros_like(image)
        out[1:-1, 1:-1] = (
            image[1:-1, :-2].astype(np.uint16)
            + image[1:-1, 2:].astype(np.uint16)
            + image[:-2, 1:-1].astype(np.uint16)
            + image[2:, 1:-1].astype(np.uint16)
        ) >> 2
        return out.astype(np.uint8)

    def update(self, dt, width, height, preset, level, bass, treble, beat_pulse=0.0):
        size = (max(2, width // 2), max(2, height // 2))
        if self.reset_pending or self.size != size:
            self.reset(size, preset)
        self.speed_gain = 1.0 + min(0.8, level * 0.45 + bass * 0.2 + treble * 0.25 + beat_pulse * 0.2)
        self.elapsed += min(dt, 0.05)
        while self.elapsed >= self.TICK_SECONDS:
            self.elapsed -= self.TICK_SECONDS
            self.life_remaining -= 1
            if self.life_remaining <= 0:
                self.cycle_count += 1
                self.reset(size, preset)
                self.speed_gain = 1.0 + min(0.8, level * 0.45 + bass * 0.2 + treble * 0.25)

            waiting = self.delay > 0
            self.delay[waiting] -= 1
            moving = ~waiting
            if moving.any():
                self.x[moving] += self.vx[moving] * self.speed_gain
                self.y[moving] += self.vy[moving] * self.speed_gain
                if self.shade:
                    faded = np.maximum(0, self.rgb[moving] - self.shade)
                    faded[faded <= 10] = 0
                    self.rgb[moving] = faded
                px = self.x[moving].astype(np.int32)
                py = self.y[moving].astype(np.int32)
                colors = self.rgb[moving].astype(np.uint8)
                valid = ((px >= 1) & (px < size[0] - 1)
                         & (py >= 1) & (py < size[1] - 1)
                         & (colors.max(axis=1) > 0))
                if valid.any():
                    np.maximum.at(self.pixels, (py[valid], px[valid]), colors[valid])
            self.pixels = self._blur_four_neighbors(self.pixels)

        audio_brightness = 1.0 + min(0.6, bass * 0.25 + level * 0.2 + beat_pulse * 0.3)
        display_pixels = np.clip(self.pixels.astype(np.float32) * audio_brightness,
                                 0, 255).astype(np.uint8)
        self.surface = pygame.surfarray.make_surface(display_pixels.transpose(1, 0, 2))
        return pygame.transform.scale(self.surface, (width, height))


class Visualizer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Life Explosion — Audio Visualizer")
        self.windowed = (1100, 720)
        self.screen = pygame.display.set_mode(self.windowed, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("DejaVu Sans", 16)
        self.big_font = pygame.font.SysFont("DejaVu Sans", 25, bold=True)
        self.audio = AudioEngine()
        self.life_field = LifeExplosionField()
        self.plugins = [LifeExplosionPlugin(self.render_life_explosion), SpectrumScopePlugin()]
        self.active_plugin_index = 0
        self.active_plugin = self.plugins[0]
        self.active_plugin.activate()
        self.presets = load_presets()
        self.preset_index = 0
        self.tile_columns = 1
        self.tile_rows = 1
        self.random_preset_order = True
        remaining = [index for index in range(len(self.presets)) if index != self.preset_index]
        self.random_preset_cycle = [self.preset_index, *random.sample(remaining, len(remaining))]
        self.random_preset_cursor = 0
        self.advance_requested = False
        self.seen_beats = 0
        self.beat_pulse = 0.0
        self.transition_from_surface = None
        self.transition_started_at = None
        self.last_display_surface = None
        self.fullscreen = False
        self.interlaced = False
        self.interlace_phase = 0
        self.interlace_cache = {}
        self.running = True
        self.hint_until = time.monotonic() + 12

    def choose_file(self):
        root = tk.Tk()
        root.withdraw()
        try:
            filename = filedialog.askopenfilename(
                title="Choose music",
                filetypes=[("Audio files", "*.wav *.flac *.ogg *.aiff *.aif"), ("All files", "*.*")])
        finally:
            root.destroy()
        if filename:
            try:
                self.audio.load(filename)
            except Exception as exc:
                root = tk.Tk(); root.withdraw()
                messagebox.showerror("Unable to play file", str(exc), parent=root)
                root.destroy()

    def load_default_track(self):
        filename = Path(__file__).resolve().parent / "assets" / "music.wav"
        if not filename.is_file():
            self.choose_file()
            return
        try:
            self.audio.load(str(filename))
        except Exception as exc:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror("Unable to play bundled track", str(exc), parent=root)
            root.destroy()
            self.choose_file()

    def switch_preset(self):
        self.begin_transition()
        self.preset_index = self.next_preset_index()
        min_width, min_height = TILE_MIN_EXTENTS.get(
            self.presets[self.preset_index].name.casefold(), (100, 100))
        max_columns = max(1, 100 // min_width)
        max_rows = max(1, 100 // min_height)
        self.tile_columns = random.randint(1, max_columns)
        self.tile_rows = random.randint(1, max_rows)
        if self.random_preset_order and self.random_preset_cycle:
            self.random_preset_cursor = (self.random_preset_cursor + 1) % len(self.random_preset_cycle)
        self.life_field.reset_pending = True

    def begin_transition(self):
        if self.last_display_surface is None:
            return
        self.transition_from_surface = self.last_display_surface.copy()
        display_size = self.screen.get_size()
        if self.transition_from_surface.get_size() != display_size:
            self.transition_from_surface = pygame.transform.scale(
                self.transition_from_surface, display_size)
        self.transition_started_at = time.monotonic()

    def switch_plugin(self):
        self.active_plugin.deactivate()
        self.active_plugin_index = (self.active_plugin_index + 1) % len(self.plugins)
        self.active_plugin = self.plugins[self.active_plugin_index]
        self.active_plugin.activate()
        self.begin_transition()

    def next_preset_index(self):
        if self.random_preset_order and self.random_preset_cycle:
            return self.random_preset_cycle[
                (self.random_preset_cursor + 1) % len(self.random_preset_cycle)]
        return (self.preset_index + 1) % len(self.presets)

    def toggle_random_preset_order(self):
        self.random_preset_order = not self.random_preset_order
        if self.random_preset_order:
            remaining = [index for index in range(len(self.presets))
                         if index != self.preset_index]
            self.random_preset_cycle = [self.preset_index, *random.sample(remaining, len(remaining))]
            self.random_preset_cursor = 0

    def draw_interlace(self, width, height):
        """Approximate the original optional TV-like interlaced drawing mode."""
        if not self.interlaced:
            return
        self.interlace_phase ^= 1
        key = (width, height)
        if key not in self.interlace_cache:
            fields = []
            for start in (0, 1):
                shade = pygame.Surface((width, height), pygame.SRCALPHA)
                for y in range(start, height, 2):
                    pygame.draw.line(shade, (0, 0, 0, 70), (0, y), (width, y))
                fields.append(shade)
            self.interlace_cache[key] = fields
        shade = self.interlace_cache[key][self.interlace_phase]
        self.screen.blit(shade, (0, 0))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed, pygame.RESIZABLE)

    def render_life_explosion(self, width, height, dt, audio):
        return self.draw_particles(dt, width, height, audio.level, audio.bass, audio.treble)

    def draw_particles(self, dt, width, height, level, bass, treble):
        current = self.presets[self.preset_index]
        previous_cycle = self.life_field.cycle_count
        tile_width = max(2, width // self.tile_columns)
        tile_height = max(2, height // self.tile_rows)
        surface = self.life_field.update(dt, tile_width, tile_height, current,
                                         level, bass, treble, self.beat_pulse)
        cycle_completed = self.life_field.cycle_count != previous_cycle
        if cycle_completed and (self.random_preset_order or self.advance_requested):
            self.advance_requested = False
            self.switch_preset()
            tile_width = max(2, width // self.tile_columns)
            tile_height = max(2, height // self.tile_rows)
            surface = self.life_field.update(0.0, tile_width, tile_height,
                                             self.presets[self.preset_index],
                                             level, bass, treble, self.beat_pulse)

        frame = pygame.Surface((width, height))
        frame.fill(BG)
        for row in range(self.tile_rows):
            y = row * tile_height
            target_height = min(tile_height, height - y)
            if target_height <= 0:
                break
            for column in range(self.tile_columns):
                x = column * tile_width
                target_width = min(tile_width, width - x)
                if target_width <= 0:
                    break
                tile_surface = surface
                if tile_surface.get_size() != (target_width, target_height):
                    tile_surface = pygame.transform.scale(
                        surface, (target_width, target_height))
                frame.blit(tile_surface, (x, y))

        return frame

    def draw(self, dt):
        width, height = self.screen.get_size()
        if SILENT_TEST_MODE:
            level = bass = treble = 0.0
            self.beat_pulse = 0.0
        else:
            level, bass, treble, beats = self.audio.update()
            if beats != self.seen_beats:
                self.seen_beats = beats
                self.beat_pulse = 1.0
            else:
                self.beat_pulse = max(0.0, self.beat_pulse - dt * 2.5)
        audio_frame = AudioFrame(
            level=level, bass=bass, treble=treble, beat_pulse=self.beat_pulse,
            spectrum=tuple(float(value) for value in self.audio.spectrum_bands),
            pcm=self.audio.latest_pcm, sample_rate=self.audio.rate,
        )
        visual = self.active_plugin.render(width, height, dt, audio_frame)
        self.screen.fill(BG)
        if self.transition_from_surface is not None:
            progress = min(1.0, (time.monotonic() - self.transition_started_at)
                           / PRESET_FADE_SECONDS)
            self.screen.blit(self.transition_from_surface, (0, 0))
            visual.set_alpha(int(255 * progress))
            self.screen.blit(visual, (0, 0))
            visual.set_alpha(None)
            if progress >= 1.0:
                self.transition_from_surface = None
                self.transition_started_at = None
        else:
            self.screen.blit(visual, (0, 0))
        self.last_display_surface = self.screen.copy()
        self.draw_interlace(width, height)
        # Audio meter and restrained status overlay.
        pygame.draw.rect(self.screen, (35, 38, 53), (24, height - 30, 180, 5), border_radius=3)
        pygame.draw.rect(self.screen, (80, 220, 250), (24, height - 30, int(180 * level), 5), border_radius=3)
        title_text = (self.presets[self.preset_index].name
                      if self.active_plugin.plugin_id == "life-explosion"
                      else self.active_plugin.name)
        title = self.big_font.render(title_text, True, (230, 235, 255))
        self.screen.blit(title, (24, 20))
        if SILENT_TEST_MODE:
            label = self.font.render("Silent review · preset life cycle follows its XPL settings",
                                     True, (175, 185, 207))
            self.screen.blit(label, (24, 54))
        else:
            state = "Playing" if self.audio.playing else "Paused / finished"
            if self.audio.muted:
                state += " · muted"
            label = self.font.render(f"{state}  ·  {self.audio.file_name}",
                                     True, (175, 185, 207))
            self.screen.blit(label, (24, 54))
        if time.monotonic() < self.hint_until:
            random_state = "on" if self.random_preset_order else "off"
            controls = (f"V visualizer   F fullscreen   I interlace   Esc quit"
                        if SILENT_TEST_MODE and self.active_plugin.plugin_id != "life-explosion" else
                        f"F fullscreen   I interlace   R random order {random_state}   N next preset   V visualizer   Esc quit"
                        if SILENT_TEST_MODE else
                        (f"O choose track   Space play/pause   S mute   V visualizer   F fullscreen   I interlace   Esc quit"
                         if self.active_plugin.plugin_id != "life-explosion" else
                         f"O choose track   Space play/pause   S mute   F fullscreen   I interlace   R random order {random_state}   N next preset   V visualizer   Esc quit"))
            text = self.font.render(controls, True, (125, 138, 165))
            self.screen.blit(text, (24, height - 58))
        pygame.display.flip()

    def run(self):
        if not SILENT_TEST_MODE:
            self.load_default_track()
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.windowed = (max(640, event.w), max(400, event.h))
                    self.screen = pygame.display.set_mode(self.windowed, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_o and not SILENT_TEST_MODE:
                        self.choose_file()
                    elif event.key == pygame.K_SPACE and not SILENT_TEST_MODE:
                        self.audio.toggle()
                    elif event.key == pygame.K_s and not SILENT_TEST_MODE:
                        self.audio.toggle_mute()
                    elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_n and self.active_plugin.plugin_id == "life-explosion":
                        self.advance_requested = True
                    elif event.key == pygame.K_v:
                        self.switch_plugin()
                    elif event.key == pygame.K_i:
                        self.interlaced = not self.interlaced
                    elif event.key == pygame.K_r and self.active_plugin.plugin_id == "life-explosion":
                        self.toggle_random_preset_order()
            self.draw(dt)
        if not SILENT_TEST_MODE:
            self.audio.stop()
        pygame.quit()


if __name__ == "__main__":
    try:
        Visualizer().run()
    except KeyboardInterrupt:
        pass
