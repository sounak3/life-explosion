# Winamp-Era and Desktop Music Visualizers

## Which engines are useful for studying or reusing visualizer code?

### Takeaway
For a multi-platform screensaver, projectM is the strongest directly reusable mature engine: it is MilkDrop-compatible, LGPL-2.1, and documents Linux, Windows, Android, macOS, and WebAssembly targets. For old-school effect ideas, inspect AVS; its modern community port is BSD-3 and exposes a composable effect chain, but is not yet a turnkey 64-bit product.

### Cited Findings
- The official projectM repository describes the library as a cross-platform MilkDrop reimplementation. It parses presets, computes beat detection/FFT from PCM, renders through OpenGL, and can render to a GL context or texture. Its current frontends are separate; the SDL frontend is the canonical viewer, and maintainers warn that current frontend builds are previews and may be incomplete. — [projectM repository and README](https://github.com/projectM-visualizer/projectm)
- projectM build documentation lists Windows, Linux, macOS, BSD, Android, and WebGL/WASM, with x86/x64/ARM/AArch64/WASM architectures; listed graphics baseline is OpenGL 3.3 or OpenGL ES 3.2 and C++14. — [projectM build/platform documentation](https://github.com/projectM-visualizer/projectm/blob/master/docs/building.rst)
- Core libprojectM is LGPL-2.1; the project explicitly says upstream/downstream components may have different licenses and each part must be checked. — [projectM license and integration notes](https://github.com/projectM-visualizer/projectm)
- Ryan Geiss's official site links MilkDrop 2.25c source and its SourceForge Git repository. SourceForge lists the MilkDrop 2 project license as BSD and project as Windows/Win32 C++. This 2.25c source release is distinct from later MilkDrop 2.25d in the Winamp distribution; do not assume later code has the same license. — [Geiss official MilkDrop page](https://www.geisswerks.com/milkdrop/); [MilkDrop 2 SourceForge project](https://sourceforge.net/projects/milkdrop2/)
- Butterchurn is an MIT-licensed WebGL implementation of MilkDrop, useful for studying preset equations, feedback/warp shaders, waves, shapes, and shader-oriented rendering that can map to desktop GPU work. It is a browser engine, not a native screensaver framework. — [Butterchurn repository](https://github.com/jberg/butterchurn)
- AVS's modern community port documents a BSD-3 license and effects such as programmable SuperScope, Dynamic Movement coordinate warps, blur, color map, Texer image effects, and effect chaining. — [vis_avs repository](https://github.com/grandchild/vis_avs)
- vis_avs builds a Winamp plugin on Windows and has an early native Linux CLI/WIP Rust frontend; most presets run, but some rare plugin effects (APEs) are unavailable. The project lists 64-bit support and a standalone port as future goals; its docs also mention a 32-bit Linux build path. — [vis_avs status and build notes](https://github.com/grandchild/vis_avs)
- A separate AVS-derived library, avs_lib, claims a portable C++20 engine, 49 effects, framework-agnostic embedding, Windows/macOS/Linux support, and MIT licensing for its port. It is based on Nullsoft AVS code, so check its MIT notice, retained upstream notices, and third-party effect provenance before copying files. It is a very small/new project and should be treated as a prototype candidate. — [avs_lib repository](https://github.com/timredfern/avs_lib)
- libvisual is a plugin-host/library architecture for applications and visualization actors. Upstream has maintenance 0.4.x and newer 0.5.x development branches. Its plugin collection is a useful effect catalogue, but is legacy C/C++ and less directly compatible with the current Python visualizer than projectM. — [libvisual upstream](https://github.com/Libvisual/libvisual); [libvisual plugin tree](https://github.com/Libvisual/libvisual/tree/master/libvisual-plugins)
- Licenses vary by component: the core library is identified as LGPL-2.1-or-later, while the plugin bundle is packaged with multiple GPL-2, GPL-3, and LGPL licenses. Audit the exact actor/plugin before incorporating it. — [Fedora libvisual license record](https://packages.fedoraproject.org/pkgs/libvisual/libvisual/); [Homebrew libvisual-plugins license record](https://formulae.brew.sh/formula/libvisual-plugins)

### Inferences
- If reusing a renderer, integrate projectM as a shared library and feed it audio; if retaining the custom Life Explosion .xpl renderer, study AVS modules and implement analogous effects rather than importing AVS preset files.
- AVS effect chains, scriptable waveform scopes, dynamic coordinate movement, blur, color operations, and image sprites are useful effect families to explore. A direct code port into this Python application may be less maintainable than implementing selected effects as focused modules.
- MilkDrop offers inspiration in feedback texture warping, per-frame/per-vertex equations, shapes/waves, and pixel shaders; preset rights are separate from renderer-source rights.

### Gaps
- I did not audit every libvisual plugin file or the full MilkDrop source archive dependency/license tree.
- projectM notes compatibility differences from original MilkDrop; specific preset support requires testing. — [projectM compatibility notes](https://github.com/projectM-visualizer/projectm/wiki)
- I did not verify projectM Android store frontends as endorsed products; upstream explicitly distinguishes third-party Android apps from supported components.

## What can be learned from presets, plug-ins, and their asset bundles?

### Takeaway
An engine's source license does not license its user-authored preset packs, textures, shaders, or third-party effects. MilkDrop presets are particularly uncertain: the Cream of the Crop repository says most lack explicit licenses and makes its own public-domain assumption, which is not a reliable permission grant for a new commercial distribution.

### Cited Findings
- projectM core deliberately ships without presets; it lists separate packs for base textures, Cream of the Crop, classic projectM, original MilkDrop 2/Winamp presets, and others. Engine and content are independently sourced. — [projectM preset distribution notes](https://github.com/projectM-visualizer/projectm)
- Cream of the Crop's LICENSE.md says most MilkDrop presets were not released with explicit licenses and each author theoretically holds copyright, then says maintainers assume public domain because packs have been freely used for decades. That is the pack maintainers' assumption, not an explicit license from every author. — [Cream of the Crop LICENSE.md](https://github.com/projectM-visualizer/presets-cream-of-the-crop/blob/master/LICENSE.md)
- Ryan Geiss's authoring guide describes .milk presets as text recipes with per-frame and per-vertex equations, custom shapes/waves, and pixel shaders; separate image textures can be referenced. — [MilkDrop preset authoring guide](https://milkdrop.org/resources/preset-authoring)
- AVS port notes external AVS Plugin Effects are not loadable in the port; some original effects were integrated or reimplemented, with provenance credited per effect. This illustrates that preset files may depend on separately licensed effects. — [vis_avs compatibility and provenance notes](https://github.com/grandchild/vis_avs)
- MilkDrop3 is a Windows continuation with additional shader/preset features, but its repository page does not establish an OSI license; do not treat GitHub source availability or age as a reuse license. — [MilkDrop3 repository](https://github.com/milkdrop2077/MilkDrop3)

### Inferences
- Use code under an explicit license and create original presets/assets, or include only individually traceable packs with clear author permission/license. Preserve required attribution and license files.
- Keep an asset manifest with source URL, author, exact license/permission, dependencies, and modifications. Do not rely on a pack-level assumption where individual creators retained rights.
- Avoid MilkDrop3-only shaders/presets unless their author/license is confirmed; test presets for engine-version support and missing texture/effect dependencies.

### Gaps
- Public project repositories do not provide a per-file verified license audit for every historical MilkDrop preset or texture.
- No rights review was made for any particular preset. Public downloadability is not permission to redistribute.

## Does software age make copying safe, and what reuse path is recommended?

### Takeaway
No: age by itself does not make code, presets, artwork, or textures free to copy, and lack of a visible notice on modern work is not proof of public-domain status. Prefer explicit license grants; public domain is a specific legal status, not a synonym for old or free-to-download.

### Cited Findings
- The U.S. Copyright Office says duration depends on factors including publication and creation date; generally, post-1978 works receive life of the author plus 70 years, and anonymous/work-for-hire works have 95-years-from-publication or 120-years-from-creation terms. — [Copyright Office duration FAQ](https://www.copyright.gov/help/faq/faq-duration.html)
- Copyright Office guidance explains that missing-notice rules depend on publication date: pre-1978 notice rules differ, while absence of notice on works published on or after March 1, 1989 does not necessarily mean public domain. — [Copyright Office Circular 22](https://www.copyright.gov/circs/circ22.pdf); [37 CFR 202.2](https://copyright.gov/title37/202/37cfr202-2.html)
- Copyright protection expires only when the applicable term ends; the Copyright Office defines public domain as work never protected or whose term ended. — [Copyright Office: What is Copyright?](https://www.copyright.gov/what-is-copyright/)
- Explicit-license examples: projectM core LGPL-2.1; Butterchurn MIT; Geiss source BSD-3; modern vis_avs BSD-3; avs_lib MIT for its stated port. Each license still has its own notice, attribution, redistribution, or copyleft conditions. — [projectM](https://github.com/projectM-visualizer/projectm); [Butterchurn](https://github.com/jberg/butterchurn); [Geiss LICENSE](https://github.com/geissomatik/geiss/blob/main/LICENSE); [vis_avs](https://github.com/grandchild/vis_avs); [avs_lib](https://github.com/timredfern/avs_lib)

### Inferences
- Practical path for future Linux/Windows/Android work: evaluate projectM or MilkDrop 2.25c as an engine/reference after validating full dependency and distribution obligations; use original content for the screensaver's identity. For permissive-code prototypes, Butterchurn MIT or Geiss BSD-3 are candidates to evaluate, while auditing their dependencies and associated content separately.
- Reimplementing an algorithm without copying source text can reduce code-copying concerns, but does not automatically resolve rights in expressive preset files, copied shader code, artwork, or distinctive names. Keep provenance records.

### Gaps
- This is a technical source/license survey, not legal advice or a jurisdiction-specific clearance. Rules may differ outside the United States.
- I did not inspect bundled binaries, submodules, or every transitive dependency/license; perform a distribution-focused license audit before shipping.
