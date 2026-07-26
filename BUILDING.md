# Building and running the launcher

The Open Town launcher is deliberately separate from the game engine. It
resolves paths relative to the bundle, validates the engine, and starts the
existing client or Windows server controller. Building this small launcher
does not turn the bundled Windows game runtime into a macOS or Linux runtime.

## Runtime compatibility

This source requires Open Town's custom Panda3D build. A compatible runtime
must import all of:

```text
panda3d.core
panda3d.otp
panda3d.toontown
pytz
```

The bundled Windows extensions are named `*.cp39-win_amd64.pyd`, so they are
bound to 64-bit CPython 3.9. Replacing Python 3.9 with a newer interpreter will
not work. To change Python versions, rebuild the custom Panda3D fork,
including `libotp` and `libtoontown`, against that Python ABI and test the full
client/server stack.

The launcher itself contains no game resources or native engine modules and
may be built with a newer compatible Python. The adjacent game still requires
its platform- and ABI-matched custom runtime. Internal `panda3d.otp`,
`panda3d.toontown`, DC identifiers, and legacy resource paths remain required
for compatibility.

## Windows

Run `Open Town Launcher.bat`. It uses the compiled launcher when present
and otherwise runs the launcher source with the bundled Python.

To build the launcher executable:

```text
Build Windows Launcher.bat
```

The output is:

```text
launcher\dist\windows\OpenTownLauncher.exe
```

This executable is only the small launcher UI. The game, resources, custom
Panda3D runtime, and Astron server remain beside it in the bundle.

Final verified Windows artifact:

```text
Size: 8,452,371 bytes
SHA-256: E8123D351F79D02358755C44F1118617ABBFEEDDB3641C229A8F51BA5B553931
```

## macOS

Build on a Mac, not on Windows:

```sh
chmod +x launcher/build_macos.sh "Open Town Launcher.command"
launcher/build_macos.sh
```

Set `OPEN_TOONTOWN_BUILD_PYTHON` if `python3` is not the desired build Python.
Set `OPEN_TOONTOWN_PYTHON` to the target-native game Python when running from
source. Those environment-variable names are retained internal compatibility
interfaces; the user-facing product name is Open Town.

This bundle has no macOS game Python/runtime. Its retained macOS Astron files
are x86_64 and were not tested in this Windows handoff. An x86_64 game stack
requires Rosetta 2 on Apple Silicon; a native Apple Silicon release requires
arm64 builds of both the custom Panda3D fork and Astron. A distributable `.app`
must also be built, signed, notarized, and tested on macOS.

## Linux

Build on the target Linux environment:

```sh
chmod +x launcher/build_linux.sh open-town-launcher.sh
launcher/build_linux.sh
```

This bundle does not currently contain `game/astron/linux/astrond`. Build
Astron on Linux and put its executable there. A target-native custom Panda3D
wheel/runtime containing the OTP and Toontown extensions is also required.

## Source validation

On any platform with a compatible runtime:

```sh
python3 launcher/src/open_toontown_launcher.py --check
```

On Windows, the equivalent bundled-runtime command is:

```text
runtime\Panda3D-1.11.0-x64\python\ppython.exe launcher\src\open_toontown_launcher.py --check
```

For releases, build and test each target on its own native CI runner. The
macOS/Linux scripts currently establish launch/build layout only; no working
macOS or Linux client/server bundle is claimed. Windows cannot create, sign,
or test a genuine macOS application, and it cannot validate Linux
graphics/library compatibility.
