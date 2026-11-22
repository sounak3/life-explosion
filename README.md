# Life Explosion Visualizer

A Linux desktop visualizer inspired by the vivid particle effects of the Life Explosion Windows screensaver. It plays a user-selected track and bundles multiple audio-reactive visualizers behind a shared plugin interface. Life Explosion renders recovered `.xpl` preset settings; Spectrum Scope is an additional built-in effect.

## Requirements

- Ubuntu or another Linux desktop with a working audio output device.
- Python 3.10 or newer and `venv` support.
- Tk support in the Python installation for the audio file picker.
- Audio playback uses the bundled `assets/music.wav` when present; otherwise the app opens a file picker. Supported formats include WAV, FLAC, OGG, and AIFF.

## Setup

From this directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Run and controls

```bash
.venv/bin/python visualizer.py
```

The app starts playback of `assets/music.wav` if available; otherwise it prompts you to choose a track. Audio level, bass, treble, and detected beats affect particle speed and brightness. Each preset keeps the cycle duration encoded by its `.xpl` life-position setting and completes that full particle-field cycle before an automatic or requested preset change. Beat timing never interrupts a cycle. **R is enabled by default** and advances through presets in shuffled order at cycle boundaries; press **R** to stop automatic changes. **N** queues a manual advance for the end of the active cycle. Preset transitions crossfade over **1 second**, drawing the new field over the previous one. Each time a preset starts, its tile grid is randomized from the smallest measured width and height across five silent simulations: maximum columns are `floor(100 / minimum width %)`, and maximum rows are `floor(100 / minimum height %)`. The app independently chooses 1 through each maximum. For example, **Big Mac** allows up to 4 columns × 2 rows; **Vagary** and **Lambent** up to 3 × 1; **Kinematic**, **Imaginary**, **Trace**, and **Zombie** up to 2 × 1. Other presets stay at 1 × 1. Press **V** to cycle bundled visualizers, **O** to choose a track, **Space** to pause or resume, **S** to mute or restore sound without stopping beat analysis, **F** or **F11** for fullscreen, **I** for the approximate interlaced mode, and **Esc** to exit. Spectrum Scope draws mirrored frequency bars from the host audio analysis; Life Explosion remains the default. See `docs/PLUGIN_BUNDLE_ARCHITECTURE.md` before adding another renderer. Resize the window for windowed mode.

## Research and Porting Notes

See [the reverse-engineering and porting notes](docs/LIFE_EXPLOSION_RESEARCH_AND_PORTING.md) for the recovered particle logic, all 22 preset cycle/coverage estimates, tiling limits, known approximations, and cross-platform plan.

## Presets

The app reads version 1.0 `.xpl` files from `assets/lifeexplosion_original/Group1/` and validates their 15 numeric settings. Static inspection of the original 32-bit Delphi screensaver recovered its 10 ms animation timer, particle initialization and delay formulas, 2,800-particle default, 400-particle color groups, RGB/radius/speed ranges, per-particle color decay, and four-neighbor bitmap filter. The renderer uses preset generation delays, dark delayed tail particles, degree-based angular motion, independent axis settings, and each preset's life-position reset interval. It remains an approximation: exact GDI pixel stamping and interlaced scan conversion have not been fully ported. The **I** mode adds an alternating scanline approximation. The original documentation describes random preset order; **R** enables that shuffled cycle by default, and transitions between presets take 1 second. Tile limits are based on each preset’s minimum measured width and height: maximum columns and rows are `floor(100 / minimum extent %)`, with randomized counts from one to each maximum. `Big Mac` allows up to 4 × 2; `Vagary` and `Lambent` up to 3 × 1; `Kinematic`, `Imaginary`, `Trace`, and `Zombie` up to 2 × 1.

The original installer was not run. Its `.xpl` files, HTML and six small JPG control illustrations were extracted from the InstallShield V3 data archive into `assets/lifeexplosion_original/`. The extracted `LifeExplosion.scr` is retained for reference and must not be executed on Linux. The JPGs illustrate the original settings controls; they are not animation textures. The temporary extractor and build files are removed after extraction.

## Troubleshooting

- If the file picker does not appear, check that Python Tk support is available.
- If the bundled track is absent, use **O** to select an audio file. If audio playback cannot start, check that the desktop audio output is available and that the file format is supported.
- If the original preset folder is missing or contains unsupported `.xpl` files, the app falls back to five built-in names with default particle settings.
- Install dependencies only in this repository’s virtual environment with `.venv/bin/python -m pip install -r requirements.txt`.
