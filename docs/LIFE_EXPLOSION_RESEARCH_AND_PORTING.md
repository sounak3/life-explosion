# Life Explosion Research and Porting Notes

This document records what has been recovered from the original Life Explosion screensaver, what the Linux implementation currently reproduces, and what remains approximate. It is the technical handoff for future Linux, Windows 64-bit, and Android versions. Keep verified facts distinct from hypotheses when extending it.

## Source Material and Safety

- assets/alifex.zip is the transferred original installer archive. It was inspected and extracted without running the Windows installer.
- assets/lifeexplosion_original/Group2/LifeExplosion.scr is the extracted Windows screensaver executable. Static inspection identifies a 32-bit Delphi PE. **Never run it on Linux or as part of routine analysis.**
- assets/lifeexplosion_original/Group1/ contains 22 version 1.0 .xpl preset files, Life Explosion.html, and six small JPGs showing settings controls. The JPGs are documentation illustrations, not animation textures.
- Static inspection indicates that the SCR generates particle animations procedurally; no conventional embedded animation/video was identified. The original installer and SCR have not been executed.

## Recovered Preset Format and Animation Logic

The loader accepts a preset when its first line is “Life Explosion preset.Version 1.0”, followed by a record of the form <name>i0.i1.…i14. (15 integer settings, with the final period and no spaces in the actual record). Files are currently sorted alphabetically by filename before loading.

The current setting indices and their use are:

| Indices | Meaning in the recovered implementation |
|---|---|
| 0–5 | Base and random range for red, green, and blue |
| 6–7 | Initial particle radius and radius range |
| 8–9 | Speed and speed range; speed-width values above 5 activate the radius/axis spread mode |
| 10 | Particle-field cycle length in 100 Hz timer ticks |
| 11 | Particle activation stride; particle index is divided by this value to stagger activation |
| 12 | Per-tick shade/colour decay |
| 13–14 | Separate X and Y angle divisors in the wide-speed mode |

Static analysis recovered a 10 ms timer (100 Hz), 2,800 particles, seven colour groups of 400, and a final 150-particle dark/delayed tail. The Linux approximation initializes particles around the field centre. In wide-speed mode it increases radius by approximately round(index / speed_width) and derives X/Y placement angles from indices 13 and 14; otherwise it uses a shared random degree angle for the starting position. Velocity components use independent random angles and a random 0–99% of the preset speed. Particles activate in index order using the stride in index 11; once active, they continue moving until the field resets. Colour fades by the shade setting, and the bitmap receives a four-neighbour quarter-sum filter each tick.

The implementation interprets index 10 as a count of 10 ms ticks. For example, Imaginary has 55 ticks, or 0.55 seconds. The complete preset cycle is honored; audio beats affect particle speed and brightness but do not interrupt a cycle. The renderer remains an approximation of the original GDI stamping, blending, and scan conversion.

## Full-Cycle Coverage Estimates

The following estimates were produced by simulating all 22 presets for five random seeds per preset at 1920×1080 with music off. The bounds track active particle coordinates over the whole lifecycle after preset shade decay and screen clipping. They are **bounding-box coverage**, not the fraction of pixels filled brightly at one instant. Random runs vary; a reported 100% means particles reached the renderer's edge, so the true offscreen extent is unknown. Music can increase motion and coverage.

| Preset | Cycle | Width reached | Height reached |
|---|---:|---:|---:|
| $ | 1.28 s | 99–100% | 100% |
| Ablation by Mixy7@aol.com | 1.57 s | 100% | 100% |
| Acclaim | 1.57 s | 100% | 100% |
| Big Mac | 2.30 s | 23–26% | 44–49% |
| Butterflies by Ensi Kay | 1.83 s | 100% | 100% |
| Cylodrome by speedy | 1.07 s | 100% | 100% |
| Dimensional | 1.87 s | 100% | 100% |
| Falusion by Kat =^,,^= | 2.82 s | 100% | 100% |
| Felicity | 2.28 s | 71–75% | 99–100% |
| Gluki | 1.24 s | 100% | 100% |
| Imaginary | 0.55 s | 39–42% | 70–75% |
| Kinematic | 2.31 s | 35–40% | 60–70% |
| Lambent | 2.31 s | 32–40% | 62–68% |
| Lonesome Star | 3.00 s | 100% | 100% |
| Macrocosm | 2.14 s | 100% | 100% |
| Massaraksh | 3.10 s | 68–81% | 100% |
| Micky Mouse by David Martin | 1.18 s | 100% | 100% |
| Peachy by Ensi Kay | 1.11 s | 92–99% | 100% |
| Rabid | 1.24 s | 100% | 100% |
| Trace | 2.25 s | 47–49% | 81–85% |
| Vagary | 1.03 s | 31–33% | 51–55% |
| Zombie | 2.12 s | 36–50% | 69–86% |

These are empirical estimates from five silent simulations, not mathematical guarantees or measurements of the Windows SCR. The renderer clips particles at the screen boundary, and music-dependent speed is absent from these estimates. Re-run with more seeds and representative audio before treating tile limits as validated for release.

## Current Linux Application Behavior

- Entry point: visualizer.py; dependencies are in requirements.txt; setup and user controls are in the root README.md.
- Python with pygame-ce renders a half-resolution particle bitmap and scales it to the display. NumPy handles particle arrays; SoundFile decodes audio; Tk provides the file chooser.
- Startup loads assets/music.wav when present, or prompts for a supported audio file. Audio analysis uses RMS level, bass/treble spectrum bands, and positive spectral flux with a 240 ms beat dead-time. Audio level/bands and beat pulses affect particle movement/brightness. **S** mutes output without stopping playback or analysis; Space pauses; O chooses a file.
- **R** is enabled by default and creates a shuffled preset cycle. It visits each preset once per cycle. With R off, advancement follows filename-sorted order. **N** queues an advance; automatic and requested changes occur only at a completed field-cycle boundary. Presets crossfade for one second, with the next field drawn over the previous image.
- Interlace (**I**) is an alternating scanline approximation. Fullscreen toggles with **F/F11**; **Esc** exits.

## Random Grid Tiling

Per-preset minimum bounding-box width and height from the five silent simulations are stored in TILE_MIN_EXTENTS in visualizer.py. On each preset start, maximum columns are floor(100 / minimum_width_percent); maximum rows are floor(100 / minimum_height_percent). The app independently randomizes each count from 1 through that maximum and repeats the same rendered field in each cell.

Current upper limits are: Big Mac 4×2; Vagary and Lambent 3×1; Kinematic, Imaginary, Trace, and Zombie 2×1. Other presets are capped at 1×1 because their observed extents reached or nearly reached the screen bounds. These limits deliberately use the minimum sampled extents, so a larger random run or strong audio may crop at cell edges. Tiling is a Linux-side presentation feature and was not found as an original SCR behavior.

## Cross-Platform Porting Direction

Keep the recovered simulation separate from windowing, audio, and operating-system integration:

1. Define a platform-neutral preset model/parser and a deterministic fixed-step particle engine. Keep the 100 Hz tick and .xpl value meanings explicit; add seeded randomness for reproducible comparisons.
2. Put drawing behind a renderer interface. Preserve screen-relative scaling, particle buffers, shade/filter behavior, cycle boundaries, crossfade, and optional grid tiling as configurable presentation behavior.
3. Put audio decode/output and analysis behind separate interfaces. The visual core should also run silently and should not depend on an audio device.
4. Keep platform shells thin. Linux currently uses pygame-ce. A Windows 64-bit release still needs a native screensaver launch/configuration/preview wrapper and installer validation; a normal fullscreen executable alone is not a complete screensaver integration. Android needs a separately researched system idle/screensaver lifecycle and audio/display integration. These platform-specific contracts have not yet been implemented or validated.
5. Compare ports using identical .xpl files, seeded particle initialization, fixed-step snapshots, and reference screenshots. Preserve the original assets and document every intentional deviation.

## Known Gaps and Next Research

- Exact GDI pixel placement, edge behavior, palette arithmetic, and interlaced scan conversion are not fully reconstructed; the current four-neighbour filter and particle rendering are approximations.
- The original documentation confirms a random-preset option, but the original default state and deterministic ordering when random mode is disabled have not been verified. The app's shuffled default and filename order are implementation choices.
- Coverage figures use five silent runs and clipped particle bounds. More seeds, audio-enabled runs, and actual screenshot measurements are needed before final tile calibration.
- Verify audio latency, pause/resume, long-file memory usage, fullscreen behavior, and tile-grid composition on each supported desktop environment.
- Do not claim that the Linux approximation is pixel-identical to the original SCR.
