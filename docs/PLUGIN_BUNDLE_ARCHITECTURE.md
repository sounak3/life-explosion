# Bundled Visualizer Architecture

The app is the host for a collection of interchangeable renderers. The host owns audio playback and analysis, keyboard input, fullscreen/windowed display, preset timing, and visual crossfades. A renderer receives an immutable AudioFrame and returns a pygame-compatible surface at the requested size.

## Current renderers

- **Life Explosion** (life-explosion) adapts the existing .xpl-driven simulation without moving its preset lifecycle into the plugin. It remains the default.
- **Spectrum Scope** (spectrum-scope) is a native pygame renderer using the same host-provided spectrum, beat pulse, and audio levels. Press **V** to switch between bundled renderers. Life Explosion simulation time pauses while another renderer is active.

Implement a renderer in this directory, expose it from visualizer_plugins/__init__.py, and register it in Visualizer.plugins. Keep audio output and user controls in the host so plugins share playback and track selection.

## Native visualizer engines

A third-party engine can fit this contract through an adapter if it can consume host audio and return a pygame surface. AudioFrame exposes normalized spectrum bands, the latest PCM chunk, and its sample rate for engines that need PCM input. Native engines that require an OpenGL context may need a shared OpenGL host or an explicit frame readback bridge; converting every frame to a pygame surface can add latency and cost.

projectM is a suitable future native backend, but is not bundled here. Its upstream project uses a C++/OpenGL rendering API and PCM input; it is not a Python pygame plugin that can be dropped into this interface directly. A projectM adapter should preserve projectM license notices and keep preset/texture licensing separate from engine code. Check the [upstream build guide](https://github.com/projectM-visualizer/projectm/blob/master/docs/building.rst) and [core API](https://github.com/projectM-visualizer/projectm/blob/master/src/api/include/projectM-4/core.h), plus runtime libraries, before integrating it.

## Licensing and assets

Review each renderer code, presets, shaders, textures, and other assets separately. A permissive engine license does not automatically cover third-party presets or media. Keep bundled assets and their license/attribution records together, and do not copy proprietary visualization packs into this repository.
