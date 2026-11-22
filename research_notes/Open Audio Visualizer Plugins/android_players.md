# Android Player Visualizers and Reuse

## What Android/Poweramp-style options exist?

### Takeaway
For MilkDrop-style animation, projectM is the strongest reusable foundation: it is an actively maintained cross-platform rendering library, and ProjectM Android is a working Android visualizer front end. Poweramp offers a separate route for *Poweramp-compatible preset packs*, but its integration API is expressly for apps that communicate with Poweramp; it is not a general license to reuse the player or its bundled visual assets.

### Cited Findings
- Poweramp currently advertises 252 built-in Milkdrop v1/v2 presets, up to 120 fps, spectrum bars, and support for user `.milk` files or preset APKs. Its official preset example explains that Poweramp translates MilkDrop EEL to Lua and HLSL shaders to GLES GLSL; this conversion is nontrivial and not every preset renders correctly. [Poweramp features](https://powerampapp.com/); [Poweramp visualization preset example](https://github.com/maxmpz/powerampapi/blob/master/poweramp_vis_presets_example/readme.md)
- The Poweramp API repository contains a visualization-preset example and says preset APKs can be installed and recognized by Poweramp. Its API license permits use for software that communicates with Poweramp/Poweramp Equalizer on Android, which makes it a fit for a Poweramp add-on, not a standalone cross-platform renderer. [Poweramp API repository](https://github.com/maxmpz/powerampapi); [API license](https://github.com/maxmpz/powerampapi/blob/master/LICENSE.txt)
- `felixpalmer/android-visualizer` is an MIT-licensed Android `View` library with waveform, frequency bars, circular waveform, and composable examples. It is a simpler spectrum/waveform source, not a MilkDrop engine. [Repository and license](https://github.com/felixpalmer/android-visualizer)
- projectM is a cross-platform MilkDrop-compatible library. The core parses presets, analyzes PCM using FFT and beat detection, and renders with OpenGL; its core library is LGPL-2.1. [Official projectM repository](https://github.com/projectM-visualizer/projectm)
- ProjectM Android is a phone/tablet and TV visualizer, not a music player. It runs the projectM engine and supports microphone or Android playback capture on phones; its docs say playback capture needs Android 10+, user consent, and a source app that permits capture. [ProjectM Android](https://github.com/johnneerdael/ProjectM-Android)

### Inferences
- A future standalone Android screensaver can integrate projectM as the rendering engine and build its own audio/player UI around it. If it plays the selected file itself, feeding decoded PCM directly to projectM avoids depending on another player exposing its output.
- For an app visualizing *other* players, Android capture restrictions matter: `Visualizer` provides only partial, low-quality samples and requires `RECORD_AUDIO`; output-mix session 0 also needs `MODIFY_AUDIO_SETTINGS`. Android playback capture instead requires user-approved MediaProjection, Android 10+, compatible usage/capture policy, and the source app must not opt out. [Visualizer API](https://developer.android.com/reference/android/media/audiofx/Visualizer); [Playback capture guide](https://developer.android.com/media/platform/av-capture)

### Gaps
- Poweramp's 252 bundled presets are not individually audited here for author, license, or redistribution permission. Do not copy them into a standalone app based only on their being bundled in Poweramp.
- I did not verify whether Poweramp currently exposes any public API for a separate app to obtain live PCM/FFT from its playback session; the linked public repository documents visualization preset packs, not a general audio-tap contract.

## Which code, presets, and assets are safely reusable?

### Takeaway
Treat the rendering engine, preset text, textures, and branding as separate works with separate rights. A repository being old, public, or widely mirrored is not a substitute for an explicit license; the most defensible route is to use code with a clear compatible license and assets with clear provenance and redistribution rights, or create original presets and textures.

### Cited Findings
- projectM's core is LGPL-2.1, which expressly allows use in closed-source applications when the library license terms are followed; integration still requires handling the license obligations and reviewing dependencies. [projectM license statement](https://github.com/projectM-visualizer/projectm)
- ProjectM Android's third-party inventory lists the projectM engine as LGPL-2.1 and identifies a bundled Cream of the Crop preset collection and textures as CC0 *as distributed by that particular project*. It also distinguishes other external test fixtures from shipping assets. [ProjectM Android third-party inventory](https://github.com/johnneerdael/ProjectM-Android/blob/main/docs/THIRD_PARTY.md)
- The upstream Cream of the Crop preset repository says most MilkDrop presets were released without a specific license, that each author theoretically holds copyright, and that it assumes public-domain status based on free release and longstanding use. That is a repository maintainer's stated assumption, not an individual license grant. [Cream of the Crop license note](https://github.com/projectM-visualizer/presets-cream-of-the-crop/blob/master/LICENSE.md)
- In the United States, most post-1977 individual-author works last for the author's life plus 70 years; anonymous, pseudonymous, and work-for-hire works generally last 95 years from publication or 120 years from creation, whichever is shorter. Exact terms vary by jurisdiction and publication history, so “old” alone does not show that a plugin, preset, image, or logo is public domain. [U.S. Copyright Office FAQ](https://copyright.gov/help/faq/faq-duration.html)
- The Poweramp API license is scoped to themes, skins, widgets, plugins, apps, and software that communicate with Poweramp on Android. Its preset example identifies `.milk` files and optional texture files as package contents, but that does not itself grant rights to third-party presets/textures. [Poweramp API license](https://github.com/maxmpz/powerampapi/blob/master/LICENSE.txt); [preset example](https://github.com/maxmpz/powerampapi/blob/master/poweramp_vis_presets_example/readme.md)

### Inferences
- Practical priority: (1) projectM engine under LGPL-2.1 for a native MilkDrop renderer; (2) original authored presets and textures under a license we choose; (3) carefully audited CC0/CC-BY asset bundles with notices; (4) Poweramp preset APKs only when building an add-on specifically for Poweramp and only after checking each asset's license.
- Reusing ideas such as a spectrum bar layout or particle behavior is different from copying source code, preset files, shader expressions, artwork, names, or logos. Build new visual scenes from the underlying general techniques and keep a source/permission record for every imported file.
- “Open-source plugin” should be checked at the repository/file level: code license does not automatically cover bundled presets, textures, fonts, screenshots, or trademarks.

### Gaps
- Rights can differ by country and individual preset author; the cited U.S. Copyright Office summary is not a jurisdiction-specific legal clearance opinion.
- This review did not inspect every file or notice in Poweramp's 252 built-in presets, legacy Winamp visualizer packs, or Android visualizer repositories.

## What should be reused for a future standalone Android screensaver?

### Takeaway
Use projectM (or its Android engine integration) for a close MilkDrop/Winamp lineage, but keep it distinct from Poweramp's player-specific preset-pack mechanism. Use direct PCM from a player inside the future app where possible; otherwise offer Android microphone or user-authorized playback capture as separate input modes with clear compatibility limits.

### Cited Findings
- The projectM library accepts PCM, performs FFT/beat analysis, and outputs OpenGL-rendered visuals; projectM identifies its SDL frontend as the canonical cross-platform viewing app. [projectM repository](https://github.com/projectM-visualizer/projectm)
- ProjectM Android's developer documentation publishes build paths and an Android core AAR, showing a real route to an Android app integration, while also documenting audio source limits and OpenGL ES requirements. [ProjectM Android repository](https://github.com/johnneerdael/ProjectM-Android)
- Android playback capture only works for eligible media/game/unknown audio, a source with capture allowed, and user-granted capture consent; protected/opted-out tracks/apps can be silent. [Android playback capture guide](https://developer.android.com/media/platform/av-capture)
- The platform `Visualizer` API exposes waveform and 8-bit FFT data and explicitly warns it is not a recording interface and returns partial, low-quality audio. [Android `Visualizer` API](https://developer.android.com/reference/android/media/audiofx/Visualizer)

### Inferences
- Cross-platform roadmap: keep visual parameters and authored scene definitions in an engine-neutral format where practical, with projectM/MilkDrop `.milk` support as a distinct compatibility backend. Android can bind libprojectM through JNI/OpenGL ES; desktop Linux/Windows can use the same core library with platform-specific window/audio capture. This avoids depending on proprietary player plug-in APIs.
- For audio reliability, expose three modes: internal player PCM (best and deterministic), Android playback capture (other eligible apps, consented), and microphone (universal fallback but affected by room noise and device processing).
- Track third-party notices and provenance alongside each preset/texture pack, and don't ship Poweramp's or other players' built-in visuals unless the rights holder grants a suitable license.

### Gaps
- The exact Android NDK/ABI build integration and current minimum device requirements should be validated against the target app and devices before implementation; this note is a reuse assessment, not a build recipe.
- Android screensaver/daydream lifecycle and store-distribution requirements were outside this player-visualizer research scope.
