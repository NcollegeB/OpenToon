# Open Town Local

This folder contains a locally configured Open Town development server,
Windows client, bundled custom Panda3D runtime, portable launcher source, a
built Windows launcher, and a server-control GUI.

This is the upstream Open Toontown stack requested in the latest setup step. It
is not a recreation of Corporate Clash and does not claim Corporate
Clash-exclusive systems or content.

## Source and file map

See `ARCHITECTURE_LAYOUT.md` for the annotated client/server architecture,
startup flow, package responsibilities, persistent data, logs, resources, and
the safest place to make each kind of change. `FULL_FILE_INDEX.txt` is the
complete point-in-time path listing (excluding `.git` internals).

See `CUSTOM_FEATURES.md` for the branding, display, skip, and gag-XP changes.
See `BUILDING.md` for launcher builds and the macOS/Linux runtime requirements.
The GitHub-ready cumulative history, exact changed-file inventory, Stinky
profile record, and project-name recommendation are under `changes\`.

## Start playing

1. Double-click `1 - Open Town Server GUI.bat`.
2. In the controller, click **Start All** and wait until Astron, UberDOG, and
   AI District each say **Running**.
3. Double-click `2 - Open Town Client.bat` or `Open Town Launcher.bat`.
4. The local development login token is `dev`. On the first run, use the
   in-game avatar chooser to create or select a Toon.

The controller has Start, Stop, and Restart buttons for the full stack and for
each service. It shows service state, PID, merged color-coded logs, save/clear
log controls, and player joins/leaves from Astron's `avatarEnter` and
`avatarExit` event records. Closing the GUI while services are active prompts
you to stop them.

## Custom gameplay and display

The client initially opens at 1920×1080 with a dynamic widescreen aspect ratio,
VSync, and an explicit 60 FPS cap. In **Options → Advanced Settings**, the
frame limit can be set to 30, 60, 120, 144, or unlimited. The same dialog
controls the FPS meter, VSync, MSAA, anisotropic filtering, music and sound
volumes, particles, and camera field of view.

The active tutorial and every trolley minigame have a bottom-right skip button.
The minigame control appears only during active play, asks for confirmation,
and requires a unanimous vote from every current participant. A completed skip
awards zero jellybeans and does not count as normal play-minigame ToonTask
completion. Gag XP is 10× in ordinary battles; an N-floor Cog building uses
exactly `(10 + N)×`, so a three-floor building uses 13×. Invasion and More-XP
holiday bonuses stack multiplicatively, and the existing per-battle XP cap
remains in force.

The Options page has separate **Advanced Settings**, **Main Menu**, and
**Exit** controls. Escape closes the top dialog or active menu, and Space
advances paged dialogue unless a text-entry field currently has focus. Caps
Lock toggles a current-ToonTasks overlay from any local-Toon gameplay state;
the overlay shows all active tasks and Escape closes it.

Ordinary public-hood fishing now has authoritative pier/target generation,
cast and target validation, catch rolls, quest-item handling, persistent fish
collection/tank updates, fisherman sales, trophies, and Laff rewards. Its 20
focused server/persistence tests pass and the AI reaches normal startup with
the path loaded. A live client catch/sale/reconnect walkthrough has not yet
been recorded. Estate-pond fishing and authoritative Fish Bingo remain
unfinished.

The 16 standard trolley minigames and Trolley Tracks have client/server source.
Their common skip path has 17 focused policy/wiring tests, and a live solo Maze
skip recorded a unanimous `1/1` vote, zero reward, and a clean playground
return. A live multi-client vote and the complete all-game cleanup matrix
remain open. See `changes\FEATURE_AUDIT.md` for the exact evidence boundary
and `changes\TODO.md` for the prioritized, checkable implementation backlog.

## Neutral presentation and compatibility boundary

The normal server configuration does not spawn the upstream named classic
characters. User-facing neighborhood, launcher, window, tutorial, catalog, and
minigame copy uses the Open Town names documented in `CUSTOM_FEATURES.md`.

Neutral embedded visual substitutions cover the catalog host and cover, Fish
Bingo marker, player-panel game logo, a catalog painting, garden statues,
Magic Bean thumbnails, the tutorial guide, Pattern Game host, maze prize,
character-shaped firework, five standalone destination signs, and the
character-branded exits embedded in 16 English street-map textures. Both
active Gag Shop signs use original neutral `GAG SHOP` artwork with no character
portrait. These substitutions reuse compatible models, nodes, textures, and
numeric IDs so the affected systems continue to load existing data.

Active world DNA was also presentation-neutralized. Displayed neighborhood,
street, cinema, and destination text uses the Open Town names; 52 active
character destination portraits use a neutral star; four displayed character
statues use a neutral planter; and the two Acorn entrance models omit only
their displayed character subtree while preserving their architecture and
collisions.

This is a presentation-layer compatibility pass, not deletion of the upstream
resource archive. Internal Python/DC identifiers, database fields, numeric
IDs, DNA group/font/storage identifiers, model-node names, legacy resource
paths, classic-character files, and unused binary nodes remain when changing
them would risk model lookup, network, or save compatibility. The existing
`toontown.ico` and `toonmono.cur` resources also remain. Their presence must not
be interpreted as rights clearance or as permission to redistribute the
resource bundle.

## Local-only security

Astron ports 7197, 7198, and 7199 are explicitly bound to `127.0.0.1`. The GUI
validates those binds and refuses to start Astron if they are exposed. This is a
development stack with development authentication; do not port-forward it or
expose it to the Internet.

The bundled game runtime uses Python 3.9 because its custom native
`panda3d.otp` and `panda3d.toontown` extensions are CPython-3.9 Windows
binaries. A newer launcher Python is supported, but the game interpreter cannot
be upgraded independently of those native modules.

## Windows launcher artifact

`Open Town Launcher.bat` prefers the bundled executable and falls back to the
launcher source when needed. The final Windows artifact is:

```text
launcher\dist\windows\OpenTownLauncher.exe
Size: 8,452,371 bytes
SHA-256: E8123D351F79D02358755C44F1118617ABBFEEDDB3641C229A8F51BA5B553931
```

The executable packages only the small launcher UI. It still requires the
adjacent `game\` and `runtime\` directories. macOS and Linux launcher/build
scripts are supplied as source, but a working game client on either platform
also requires target-native custom Panda3D modules and Astron. Those native
game stacks were not built or tested on this Windows machine.

## Logs and data

- Merged live server log: displayed in the GUI; use **Save Log** for a copy.
- Astron event logs: `game\astron\logs\events-*.log`
- Astron database: `game\astron\databases\astrondb`
- Development accounts: `game\astron\databases\accounts.json`
- Client logs: `game\logs\toontown-*.log`
- AI data: `game\data`

Stop all services before copying or backing up the database.

## Verification and provenance

`Test Server Lifecycle.bat` performs a non-GUI test that starts
Astron → UberDOG → AI, checks unique PIDs and loopback ports, then always stops
AI → UberDOG → Astron and confirms the ports closed.

The normal GUI also refuses to start a second Astron instance when local ports
7197–7199 are occupied. UberDOG and AI use Windows break handlers so Stop and
Restart exit through Python normally; the controller waits for explicit ready
records before marking them Running.

Installed source revisions:

- Open Toontown `develop`: `a5ecbb8b1eba76601c896ffe9503050a8e5c12c4`
- Open Toontown resources: `d8c73a9978633979ddf2ef8813f0152037a0d978`

The custom Panda3D installer used for this setup was the x64 installer linked
by the Open Toontown setup documentation. It is not Authenticode-signed and no
maintainer-published SHA-256 was available. This downloaded copy was scanned
with active Microsoft Defender before installation; no detections were
reported. Its locally recorded SHA-256 is:

`0F6C12D42729D2265D0DAB152C88EEAC9EDE021C1043CBFEB4CA8508E5979CA0`

## Licensing notice

Open Toontown's code is distributed under its BSD 3-Clause license; see
`game\LICENSE`. The separate resources repository states that its extracted
Toontown Online assets have no license and remain property of The Walt Disney
Company; see `game\resources\README.md`.

This assembled copy is for local reference/testing only. Do not redistribute
the asset bundle or present it as an original, rights-cleared game.
