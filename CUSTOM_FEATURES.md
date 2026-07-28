# Open Town custom feature map

This document describes the local modifications layered onto the upstream Open
Toontown source. Open Town is the user-facing name. Internal Python class
names, distributed-class identifiers, numeric IDs, database fields, model-node
names, and legacy resource paths intentionally remain when changing them would
break network, save, DNA, or model compatibility.

## Branding and character behavior

The eight hood AI loaders now default `want-classic-characters` to false. The
legacy distributed classes remain in `toon.dc`, but the named classic
characters are not generated during normal server startup.

`game\otp\otpbase\NeutralBranding.py` transforms user-facing localizer values
after the English localizers load. It does not rewrite resource paths,
dictionary keys, the copyrighted-name denylist, or botanical Daisy strings.

| Legacy display name | Open Town display name |
|---|---|
| Toontown Central | Central Commons |
| Donald's Dock | Anchor Bay |
| Daisy Gardens | Bloom Gardens |
| Minnie's Melodyland | Melody Meadows |
| Donald's Dreamland | Moonlight Meadows |
| Goofy Speedway | Turbo Speedway |
| Chip 'n Dale's Acorn Acres | Acorn Acres |
| Chip 'n Dale's MiniGolf | Acorn MiniGolf |

Five standalone destination signs and the character-branded exit icons baked
into 16 English street-map textures were replaced with neutral artwork. The
tutorial uses a generic Toon guide, Pattern Game uses a generic Dance Coach,
the maze prize is a jellybean, and the character-shaped firework uses three
neutral bursts while retaining its existing numeric protocol ID.

The two active Gag Shop sign textures now use original neutral `GAG SHOP`
artwork with no character portrait. Player-visible text says **Gag Shop**.
Existing BAM names, texture slots, interior identifiers, collisions, and shop
logic remain unchanged for compatibility.

### Embedded UI and model substitutions

The following active presentation paths no longer render their character-
branded upstream visuals:

- The catalog host is a generic Toon named **Catalog Guide**; its cover uses a
  neutral `CATALOG` title without the former portrait.
- Fish Bingo uses the existing boot-shaped marker.
- Player information panels expose only the neutral unknown-game logo.
- The legacy catalog character painting uses the existing flower artwork.
- Character garden statues use the existing neutral pedestal, while Magic
  Bean thumbnails use the existing sack model.
- The tutorial guide, Dance Coach, maze jellybean, and three-burst firework
  replace the active character-specific presentation in those systems.
- Active DNA text baselines use neutral neighborhood, street, destination, and
  cinema names. Active character destination portrait model paths resolve to
  a neutral star, and displayed landmark model paths resolve to a neutral
  planter.
- The two Acorn entrance BAM variants remove only the displayed character
  subtree. Their architecture and all collision nodes/solids are retained.

The substitutions deliberately preserve catalog item IDs, plant/special IDs,
prices, saved inventory meaning, DC class order, and firework type number.
Legacy-named local variables and unused nodes may therefore remain internally.

`game\otp\otpbase\NeutralResources.py` deterministically generates the
resource substitutions under `game\open_town_assets`. The generated overlay is
loaded before the separate upstream resource snapshot, is verified during
setup, and is recreated by the client when missing.

Internal DNA group names, font/storage codes, filenames, legacy model paths,
classic-character resources/classes, unused binary nodes, and the legacy
icon/cursor resources remain in the archive. Deleting or renumbering them
without purpose-built replacements and migration work would risk runtime or
saved-data compatibility. The active displayed DNA text/graphics are
neutralized; the retained resource pack is not rights-cleared for
redistribution. See the licensing notice in `README_LOCAL.md`.

## Gag XP

Authoritative reward logic is in:

- `game\toontown\battle\BattleCalculatorAI.py`
- `game\toontown\battle\DistributedBattleBaseAI.py`
- `game\toontown\building\DistributedSuitInteriorAI.py`
- `game\toontown\cogdominium\DistributedCogdoInteriorAI.py`
- `game\toontown\toonbase\ToontownBattleGlobals.py`

Client display mirroring is in:

- `game\toontown\building\DistributedSuitInterior.py`
- `game\toontown\toon\InventoryNew.py`
- `game\toontown\town\TownBattle.py`

Ordinary battles use 10× gag XP. A building with `N` total floors uses
`10 + N`, independent of the current floor. Invasion and More-XP holiday
bonuses multiply that result exactly once. Cogdo floor credit also combines
with the 10× base and each active global bonus exactly once. The existing
attack-credit cap of 200 is unchanged.

## Skip buttons

`game\toontown\tutorial\TutorialManager.py` creates the bottom-right tutorial
skip button. It is enabled only while the tutorial place is in its safe `walk`
state. Once the server authorizes the skip, the client starts the normal
Central Commons `teleportOut` transition before sending `stopTutorial`; this
avoids the stale tutorial trolley-quest acknowledgement path while retaining
the existing quest update and cleanup.

`game\toontown\minigame\DistributedMinigame.py` creates the common bottom-right
minigame skip button only during active `frameworkGame` play. It opens a
localized Yes/No confirmation and shows the current vote count/status.
`DistributedMinigameAI.py` validates that the sender is a participant, rejects
pre-play/cleanup states, ignores duplicate requests, and waits for every unique
current participant to vote. A completed unanimous skip assigns zero reward to
every participant.

Play-minigame ToonTask credit is no longer awarded when the game is created.
It is granted once for normal, non-skipped completion before the client-exit
barrier; an explicit skip does not count. Known early-abort fields in Toon
Escape, Maze Game, and Treasure Dive now have cleanup guards. This common path
covers the 16 normal trolley games and Trolley Tracks, but not racing, golf,
Cogdo, party, picnic-table, fishing, or estate activities.

Focused cleanup also covers Diving collision/control teardown, TwoD
tasks/events/masks, Ring's ending task, Race tasks/intervals/dice, and delayed
Target/Photo work. Live solo and two-player Maze skips returned cleanly with
zero rewards; the two-player vote advanced from `1/2` to unanimous `2/2`. See
`changes\FEATURE_AUDIT.md` for the remaining four-player and all-game cleanup
validation.

## Ordinary hood fishing

`game\toontown\ai\FishManagerAI.py` is the authoritative ordinary-fishing
manager. `ToontownAIRepository.py` creates it, recursively generates public
hood piers from pond DNA, and populates each pond with moving targets.
`DistributedFishingSpotAI.py` validates pier ownership, cast parameters, rod,
jellybean cost, tank capacity, pending-cast state, flight timing, and target
distance before awarding a catch.

Catches can produce quest items, fish, jellybeans, or boots. Fish update the
persistent collection and tank; existing fisherman interactions use the
manager to award sale value, clear the tank, and grant newly earned fishing
trophies and Laff. Requested fish are accepted only when the current rod can
catch them. Client target checks use X/Y distance across the pond plane, so a
target's below-surface Z position does not turn a valid cast into a miss.

This implementation is scoped to ordinary public hood ponds. Estate-pond
fishing and authoritative Fish Bingo are still open. A live Party Clown Fish
catch persisted collection `1`, tank `1`, and value `6` through reconnect;
Fisherman Freddy then sold the tank, and another reconnect retained collection
`1`, tank `0`, and the capped wallet value of `40`.

## Display and settings

`game\etc\Configrc.prc`, `ToonBase.py`, `DisplayOptions.py`, and
`DisplaySettingsDialog.py` provide a 1920×1080 default, dynamic window aspect
ratio, VSync, and a 60 FPS default cap. `GraphicsOptionsDialog.py` is linked
from the normal Options page and persists:

- 30, 60, 120, 144, or unlimited frame rate
- FPS meter
- VSync
- 0×, 2×, 4×, or 8× MSAA
- 1×, 2×, 4×, 8×, or 16× anisotropic filtering
- independent music and sound-effect volume
- particles
- 45° through 90° camera field of view

Frame limit, FPS meter, volume, particles, and FOV apply live. VSync, MSAA, and
anisotropic filtering are saved for the next client start.

## Menus and keyboard

The Options page now has three distinct controls: **Advanced Settings**,
**Main Menu**, and **Exit**. Main Menu uses the normal disconnect/avatar-
chooser flow; Exit uses a separate confirmation and closes the client.

The avatar chooser's former Quit label now reads **Exit**. Its background is
attached to the aspect-aware 2-D graph with a neutral widescreen side fill, so
the original art remains centered without exposing an unrendered border at
16:9.

`game\otp\otpgui\KeyboardShortcutManager.py` is the central keyboard router:

- Escape dismisses the top visible DirectDialog first, preferring Cancel or No
  where available, then runs only the highest-priority active menu callback.
- Space advances the newest active paged dialogue.
- Caps Lock toggles the global current-ToonTasks overlay.
- Focused text-entry fields retain their normal Escape/Space behavior.
- Background chat focus is suspended during paged dialogue and restored when
  the dialogue ends.

`game\toontown\quest\QuestOverlay.py` provides the independent quest view. It
uses the Shticker Book's quest-poster renderer, displays every active ToonTask
up to the four-task carry limit, refreshes when quest data changes, and remains
registered across playgrounds, interiors, battles, activities, minigames, and
transition states. Caps Lock toggles it and Escape closes it. Foreground text
entries keep Caps Lock for normal typing.

## Launchers and server controller

- `Open Town Launcher.bat`: compiled Windows launcher with source fallback
- `launcher\dist\windows\OpenTownLauncher.exe`: built Windows launcher
- `Build Windows Launcher.bat`: reproducible Windows build
- `Open Town Launcher.command`: macOS source/built-launcher entry
- `open-town-launcher.sh`: Linux source/built-launcher entry
- `1 - Open Town Server GUI.bat`: server controller
- `2 - Open Town Client.bat`: direct Windows client

The final Windows launcher is 8,452,371 bytes with SHA-256:

```text
E8123D351F79D02358755C44F1118617ABBFEEDDB3641C229A8F51BA5B553931
```

The server controller starts, stops, and restarts Astron, UberDOG, and the AI
district; shows merged logs, service state, PIDs, and player joins/leaves; and
can save or clear its display. `Test Server Lifecycle.bat` performs a non-GUI
ordered lifecycle test.

The Windows runtime and launcher are built and tested. The macOS/Linux build
scripts package the launcher only; they do not convert the bundled
CPython-3.9 Windows game extensions. A usable client/server stack must be
built and tested on each target operating system with target-native custom
Panda3D and Astron binaries. See `BUILDING.md`.
