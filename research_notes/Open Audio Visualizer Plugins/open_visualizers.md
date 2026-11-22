# Open-Source Audio Visualizers and Reusable Ideas

## Which projects are the strongest references or reuse candidates?

### Takeaway

For a future Linux/Windows/Android product, **projectM is the strongest native cross-platform engine reference**; **Butterchurn is the clearest permissive-license WebGL route**; and **CAVA plus GLava offer narrower audio-analysis and GLSL effect examples**. None is a drop-in way to reproduce Life Explosion: MilkDrop is a different preset language and rendering model.

### Cited Findings

- **projectM** is an actively developed MilkDrop-compatible C++ library; the official repository was updated October 6, 2026. The library parses presets, analyzes PCM with beat detection and FFT, and renders to an OpenGL context or texture. It receives PCM from its host rather than capturing audio itself. Core library license is LGPL-2.1; the project specifically recommends shared-library use for compatibility/compliance. [Repository and README](https://github.com/projectM-visualizer/projectm) · [license/build/platform documentation](https://github.com/projectM-visualizer/projectm/blob/master/docs/building.rst)
- projectM documents builds for Windows, Linux, Android, macOS, BSD, and WebAssembly, with C++14 and OpenGL 3.3 or OpenGL ES 3.2 requirements. This is a credible future common engine direction, but would mean a substantial native-renderer port from the current Python/pygame implementation. [Official platform/build guide](https://github.com/projectM-visualizer/projectm/blob/master/docs/building.rst)
- The separate official [SDL frontend](https://github.com/projectM-visualizer/frontend-sdl-cpp) is a standalone audio visualizer, but it has its own GPL-3.0 license; the projectM core and frontend licenses must not be conflated. The current release page advertises Windows 64-bit ZIP and Linux x86_64 packages, but says those bundles are not production-ready/package-manager releases. [Frontend repository](https://github.com/projectM-visualizer/frontend-sdl-cpp) · [releases](https://github.com/projectM-visualizer/frontend-sdl-cpp/releases)
- **Butterchurn** is a WebGL implementation of MilkDrop and has an MIT-licensed engine. Its API accepts an audio node and canvas; it exposes renderer resizing and timed preset blending. Its README says it requires WebGL 2. This is a practical reference for a browser/WebView-based visualizer and shader/preset transitions, but not a native Python library. [Repository/API and license](https://github.com/jberg/butterchurn) · [MIT license](https://raw.githubusercontent.com/jberg/butterchurn/master/LICENSE)
- **Butterchurn presets** are distributed in a separate repository, also with a repository-level MIT license. They are converted community MilkDrop presets, however; the README thanks preset authors and the source provenance is different from the rendering engine. Check collection and individual preset provenance/license before redistributing particular presets. [Preset repository](https://github.com/jberg/butterchurn-presets) · [preset license file](https://raw.githubusercontent.com/jberg/butterchurn-presets/master/LICENSE)
- **CAVA** is an MIT-licensed terminal/SDL spectrum visualizer, with Linux, Windows, macOS and BSD support, audio backends, configurable frequency bands, and a `cavacore` library/raw output useful for separating analysis from drawing. It is a useful reference for spectrum smoothing, audio capture interfaces, and compact visual meters, not a particle/scene engine. A June 2026 open issue questions the licensing consequences of its FFTW3 dependency for closed-source downstream use; investigate the selected FFT dependency/build before adopting code. [Repository/docs](https://github.com/karlstav/cava) · [MIT license](https://raw.githubusercontent.com/karlstav/cava/master/LICENSE) · [FFTW licensing issue](https://github.com/karlstav/cava/issues/778)
- **GLava** is a configurable OpenGL/GLSL spectrum visualizer for X11, PulseAudio and Linux/BSD. Its shader modules show radial, waveform, and spectrum techniques that can inform new effects. It is GPL-3.0, with specified imported MIT-origin files relicensed under GPL-3.0; it is Linux/X11-specific and less suitable as code to embed into a cross-platform proprietary or permissively licensed app. [Repository, modules and license notes](https://github.com/jarcode-foss/glava)
- For Android research, [ProjectM-Android](https://github.com/johnneerdael/ProjectM-Android) is a current open-source implementation/fork based on projectM. Its README states app code is LGPL-2.1 and bundled preset/texture collection is CC0; its third-party notice lists sources. This is useful porting/build/packaging evidence, but it is a downstream project, not an upstream guarantee.
- [Webamp](https://github.com/captbaritone/webamp) is a MIT-licensed Winamp 2 browser reimplementation and lists Butterchurn integration. It is useful as a reference for a player/visualizer interface or web distribution, not a screen-saver rendering engine.

### Inferences

- Minimal-change learning path: study CAVA’s audio-band processing, then apply original implementation ideas from projectM/Butterchurn (feedback, shader warping, beat-driven parameter changes) as inspiration, while implementing the visual behavior in the current renderer. Keep any reused snippets and license notices auditable.
- Cross-platform architecture path: separate audio capture/PCM and analysis from a renderer API. If replacing the Python renderer later, evaluate libprojectM via a shared library/FFI on desktop and GLES on Android; use Butterchurn only if a WebView/WebGL stack is acceptable.
- A preset engine is not the same thing as a preset collection. Reusing an LGPL/MIT engine does not automatically clear the art, image textures, shader code or individual presets that ship beside it.

### Gaps

- No code was built or benchmarked against this project. Actual integration cost, Android audio routing, GPU/performance behavior on the Dell laptop, and preset-by-preset compatibility require a prototype.
- Repository activity is a point-in-time observation for this review; it can change. License review here is triage, not legal advice.

## What transferable effects and design techniques are relevant?

### Takeaway

MilkDrop-style visualizers provide transferable *techniques* rather than Life Explosion’s specific algorithm: feedback/recursive warping, shader-based color and geometry, audio feature modulation, procedural shapes/waves, and blended scene transitions. These ideas can be reimplemented independently without copying a specific creator’s preset artwork.

### Cited Findings

- projectM describes MilkDrop presets as pixel shaders plus equations/parameters; its library evaluates those equations, uses audio beat/FFT data, and renders visuals through OpenGL. This is a programmable procedural-rendering model, quite different from the Life Explosion `.xpl` particle parameters. [projectM README](https://github.com/projectM-visualizer/projectm)
- Ryan Geiss’s MilkDrop preset-authoring reference documents per-frame and per-vertex equations, persistent variables, custom shapes/waves, and pixel shaders, making it a useful technical guide to the kinds of authorable visual behavior available. [Preset-authoring guide](https://milkdrop.org/resources/preset-authoring)
- Butterchurn’s `loadPreset(preset, blendTime)` API accepts a blend duration in seconds. Its render loop and WebGL implementation are useful references for continuously animated shader presets and scene blending. [API/readme](https://github.com/jberg/butterchurn)
- GLava’s repository includes GLSL shader modules and audio-reactive input plumbing; its documentation describes output modules/configuration and performance considerations, including CPU FFT cost in its default setup. [GLava](https://github.com/jarcode-foss/glava)
- MilkDrop 3’s author describes beat-triggered hard cuts and injected beat effects, among many transition types. This documents a useful interaction pattern—beats can affect local effect intensity separately from preset lifetime—but MilkDrop 3 itself is not established here as an open-source reuse source. [MilkDrop 3 repository feature documentation](https://github.com/milkdrop2077/MilkDrop3)

### Inferences

- For this project’s no-mid-cycle-cut requirement, beat input can modulate particle speed, brightness, color and burst strength continuously while preset changes remain tied to each `.xpl` cycle end. MilkDrop’s separate beat-effect versus preset-switch model supports this design conceptually.
- A future effect library could define independent layers: audio features (RMS, low/mid/high bands, onset), scene-specific motion/color functions, feedback/post-processing, and transitions. That preserves the recovered Life Explosion cycle logic while permitting new shader-inspired effects.
- For a Windows/Android port, GLSL/OpenGL ES techniques can be shared more readily than pygame-specific drawing, but shader capability and extensions must be tested on target devices.

### Gaps

- The cited projects do not establish that their visual styles or preset artworks are legally reusable as assets in this application. Similarity of technique does not establish permission to copy a particular shader/preset or texture.
- Effect parity was not experimentally compared; the Life Explosion renderer and projectM use different timing and preset semantics.

## Does being old make a plugin or its content safe to copy?

### Takeaway

**No. Age by itself does not put code, presets, or textures in the public domain or eliminate copyright exposure.** Prefer an explicit license that covers the exact material being reused, and track engine code separately from bundled visual assets and preset-authors’ work.

### Cited Findings

- The U.S. Copyright Office says copyright protection generally begins automatically when a work is fixed; for most post-1977 works it lasts for the author’s life plus 70 years, with different 95/120-year terms for work-for-hire, anonymous and pseudonymous works. Old software from the 1990s/2000s is therefore not automatically free to copy. [Copyright duration FAQ](https://www.copyright.gov/help/faq/faq-duration.html) · [copyright attaches automatically](https://www.copyright.gov/help/faq/faq-general.html)
- projectM’s official Cream of the Crop preset-pack `LICENSE.md` candidly says individual preset authors theoretically hold full copyright because most presets were not issued under a specific license; its assumption that they are public domain is based on longstanding free distribution and use, and it offers removal on request. Treat this as the curator’s position, not as a blanket license from every creator. [Exact pack license statement](https://raw.githubusercontent.com/projectM-visualizer/presets-cream-of-the-crop/master/LICENSE.md)
- The MilkDrop engine’s code license, a preset pack’s license, and texture/image rights are separate checks. projectM itself distributes its engine without presets and points users to separate repositories and a separate texture pack. [projectM preset-pack documentation](https://github.com/projectM-visualizer/projectm)
- The CAVA core declares MIT terms, but a current licensing issue alleges a dependency complication with FFTW3. This illustrates why one repository badge alone may not resolve the license stack of a build or derived application. [CAVA license](https://raw.githubusercontent.com/karlstav/cava/master/LICENSE) · [open dependency-license discussion](https://github.com/karlstav/cava/issues/778)
- In the United States, the Copyright Office says copyright notice/registration is generally not required for copyright to exist. The absence of a visible copyright notice is not proof that a work is unprotected. [Copyright Office FAQ](https://www.copyright.gov/help/faq/faq-general.html)

### Inferences

- The most defensible reuse workflow is to use code with explicit repository-level licenses, preserve required notices/source offers, inventory dependencies, and obtain explicit permission or choose independently authored assets when individual preset/texture licenses are missing or ambiguous.
- For MilkDrop-derived content, preserve author names and preset source metadata. For a commercially distributed multi-platform screensaver, do not rely solely on “old,” “widely used,” or a curator’s public-domain assumption.
- Descriptive concepts and general techniques (for example, particles accelerating with bass, spatial tiling, fade-over transitions) can guide an original implementation; copying specific source code, shader text, images, or distinctive preset content needs a license/right covering it.

### Gaps

- Copyright exceptions, public-domain status and license enforceability vary by jurisdiction and facts; this note does not determine status for any individual MilkDrop preset or texture. Get permission or qualified legal review for a commercial release where the rights are unclear.
