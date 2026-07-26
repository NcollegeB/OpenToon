# Third-party notices

OpenToon is NcollegeB's modification of the Open Toontown source project.

## Open Toontown source

The source under `game/` is derived from
[Open Toontown](https://github.com/open-toontown/open-toontown). That source
remains available under the BSD 3-Clause License:

- Copyright (c) 2019, Open Toontown
- License: [`game/LICENSE`](game/LICENSE)
- Upstream revision used by this project: `a5ecbb8b1eba76601c896ffe9503050a8e5c12c4`

The root MIT License does not replace or supersede the Open Toontown license.

## Resource files

Game resources are not distributed in this repository. The separate upstream
resource repository states that its extracted assets do not have an
open-source license and remain the property of their respective owner.
Accordingly, those files are not covered by this project's MIT License.

Anyone adding resources to a local checkout is responsible for making sure
they have the right to use and distribute them.

## Runtime and native components

Bundled Python, Panda3D, Astron, FFmpeg, FMOD, NVIDIA Cg, and other native
runtime components are not distributed in this source repository. Obtain or
build compatible components separately and follow their respective licenses.

## Magic Word Manager files

The following retained files identify themselves as the Toontown Offline Magic
Word Manager, Copyright 2020 Toontown Offline, and licensed under the MIT
License:

- `game/toontown/spellbook/MagicWordConfig.py`
- `game/toontown/spellbook/MagicWordIndex.py`
- `game/toontown/spellbook/ToontownMagicWordManager.py`
- `game/toontown/spellbook/ToontownMagicWordManagerAI.py`

Their source headers credit Benjamin Frisby, John Cote, Ruby Lord, Frank, Nick,
Little Cat, and Ooowoo. Those notices remain with the files.

## OpenToon additions

Original OpenToon launcher, tooling, documentation, and modifications authored
for this repository are made available by NcollegeB under the root
[`LICENSE`](LICENSE), except where a file or directory carries another notice.

OpenToon is an independent community modification. The Open Toontown name is
used only to identify the upstream source project.
