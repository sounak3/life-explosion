# Repository Guidelines

## Project Structure & Module Organization

This is a Python desktop visualizer. The entry point is visualizer.py; dependencies are listed in requirements.txt. Bundled renderer contracts and built-in visualizers live in visualizer_plugins/. Original .xpl presets, reference documentation, and the extracted Windows SCR are under assets/lifeexplosion_original/. The sample track is assets/music.wav. Reverse-engineering findings and cross-platform porting guidance are in docs/LIFE_EXPLOSION_RESEARCH_AND_PORTING.md.

## Build, Test, and Development Commands

Create the project environment and install dependencies locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python visualizer.py
```

There is no automated test suite yet. Keep dependencies inside .venv and document any new setup commands in README.md.

## Coding Style & Naming Conventions

Use Python 3.10+ conventions, four-space indentation, descriptive names, and focused functions. Keep the particle simulation's fixed 100 Hz timing and preset values explicit. Explain any change to recovered behavior in the technical notes and README.

## Testing Guidelines

No test framework is configured. For changes to rendering, timing, audio, or preset parsing, validate the affected behavior manually and record the conditions. Prefer deterministic random seeds for comparisons where practical; do not make tests depend on local audio devices.

## Commit & Pull Request Guidelines

Use short, imperative commit subjects (for example, Add preset cycle validation). Pull requests should describe motivation, implementation, and verification; include screenshots for visual changes and link issues when applicable.

## Security & Configuration

Do not execute assets/lifeexplosion_original/Group2/LifeExplosion.scr or the original Windows installer. Keep generated files in the repository or its virtual environment, and keep credentials and machine-specific configuration out of version control.
