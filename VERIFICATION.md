# Open Town Local verification record

Verified on Windows across 2026-07-25 and 2026-07-26 from the final bundle
location. This record contains automated, headless, server-startup, and live
interactive checks. Each dated section states its own live-validation
boundary.

## Automated server lifecycle

`game\win32\start_server_gui.bat --self-test --timeout 60` exited with code 0.
It verified:

- Astron started and opened its loopback message-director/client-agent ports.
- UberDOG reached `UberDOG server is ready.`
- AI reached `ToontownAIRepository: Done.`
- Astron, UberDOG, and AI used three unique live PIDs.
- TCP ports 7198 and 7199 opened on `127.0.0.1`.
- Cleanup stopped AI → UberDOG → Astron.
- All child processes exited and ports 7198/7199 closed after the test.

UberDOG and AI exited through their Windows break handlers; Astron accepted its
interrupt and exited. The final Astron configuration binds UDP 7197 and TCP
7198/7199 to `127.0.0.1`.

AI startup emits several upstream building-door/path warnings, but it still
reaches its explicit ready record.

## Source and runtime integrity

- The 2026-07-25 integrity pass AST-parsed all 1,849 Python files then present
  in `game\` with the bundled CPython 3.9 runtime.
- Runtime imports passed for `panda3d.core`, `panda3d.otp`,
  `panda3d.toontown`, and `pytz`.
- `git diff --check` reported no whitespace errors; Git printed only expected
  Windows LF/CRLF conversion notices.
- The client entry forces `GAME_SERVER=127.0.0.1`, and the configured
  development token remains `dev`.

## Neutral presentation regression checks

- The user-facing exact/CamelCase localizer scan returned zero targeted legacy
  character/brand hits.
- The copyrighted-name validation denylist and botanical Daisy species/funny
  names remained unchanged.
- All eight affected hood AI loaders default the named classic-character spawn
  guard to off.
- Headless tutorial playback parsed all 48 `tutorial_guide` commands and built
  three chapter event groups without localizer/eval failures.
- The generic Pattern Game Toon loaded valid `up`, `left`, `down`, and `right`
  animations.
- Headless/import/model-table checks passed for the Pattern Game, maze prize,
  triple-burst firework, Catalog Guide lifecycle, Fish Bingo marker, garden
  substitutions, catalog painting, player-panel logo, and neutral map/sign
  assets.
- All 93 DNA files and 1,288 baseline blocks were structurally scanned. Active
  text baselines contained zero targeted legacy names or titles.
- All 52 active character destination graphic uses resolve through
  `neutralSZ`; all four displayed landmark statues resolve through
  `prop_neutral_landmark`.
- Panda3D loaded all 27 affected zones with their real storage stacks.
- Both Acorn entrance variants omit the displayed character subtree while
  retaining all three collision nodes and all 147 collision solids.

These checks cover active substitutions. They do not assert that the upstream
resource archive is empty of legacy names or binaries. Compatibility-sensitive
DC identifiers, numeric IDs, resource paths, DNA group/font/storage names,
classic-character files, unused model nodes, and icon/cursor resources
intentionally remain.

## Display and settings checks

- The headless engine buffer opened at exactly 1920×1080 with aspect ratio
  `1.777777`.
- The default configuration loaded VSync and a 60 FPS limited clock.
- Measured limiter checks produced approximately 29.55, 60, 120, and 144 FPS
  for the corresponding choices; unlimited mode switched to the normal clock.
- The offscreen Advanced Settings test found all nine controls and verified
  persistence plus the live-apply callback.
- Static/import checks covered dynamic aspect handling and the expanded
  720p/1080p/1440p/4K resolution list.
- The live client opened at 1920×1080, exposed all nine Advanced Settings
  controls, showed the 60 FPS selection, and measured 58.0–58.2 FPS under the
  cap. The final client log contained no traceback/fatal pattern.

## Gameplay-rule checks

- Runtime assertions returned 10 for the ordinary gag-XP multiplier and 13 for
  a three-floor building; standard buildings were checked across one through
  five floors.
- Server/client integration review confirmed normal/facility/building
  multipliers use the same 10× base, while invasion and More-XP holiday
  multipliers stack and the existing 200-credit battle cap remains.
- A focused Cogdo test returned exactly
  `80 = 10 base × 2.0 floor credit × 2 invasion × 2 holiday`; invasion and
  holiday were each evaluated once.
- Live tutorial skipping initially exposed a stale trolley-quest
  acknowledgement path. The final implementation starts the normal Central
  Commons `teleportOut` transition before `stopTutorial`; its exact payload and
  call order passed a focused test, and the existing Toon reconnected in zone
  22000 without an account/avatar reset.
- The 2026-07-25 minigame skip implementation validated participant and
  framework state, ignored duplicate requests, ended the shared game, and
  assigned `[0, 0]` rewards in a two-player focused test. The single-request
  group policy was superseded by the unanimous policy recorded below.

## Live Windows walkthrough

- The packaged `OpenTownLauncher.exe` opened as **Open Town Launcher**.
- **Validate Runtime** reported Python 3.9.13 and Panda3D 1.11.0.
- **Start Client** opened the **Open Town** client at 1920×1080.
- The existing Toon entered Central Commons. The updated Turbo Speedway text
  and neutral planter were present in the live zone.
- **Options → Advanced Settings** displayed frame limit, FPS meter, VSync,
  MSAA, texture filtering, music volume, sound-effects volume, particles, and
  field of view.
- The server GUI tracked the named avatar join/leave events and displayed one
  online player.
- **Restart All** stopped and restarted Astron, UberDOG, and AI District with
  new PIDs. All three returned to **Running**, the client received the expected
  district-reset notice, and reconnecting returned the Toon to a playable
  Central Commons state.
- The final handoff leaves the server controller/services, launcher, and
  playable Windows client running for local testing.

## Windows launcher artifact

Both the launcher source and frozen executable completed `--check` with exit
code 0 and resolved:

```text
Python: 3.9.13
Panda3D: 1.11.0
Runtime: runtime\Panda3D-1.11.0-x64\python\ppython.exe
```

Final artifact:

```text
launcher\dist\windows\OpenTownLauncher.exe
Size: 8,452,371 bytes
SHA-256: E8123D351F79D02358755C44F1118617ABBFEEDDB3641C229A8F51BA5B553931
```

## 2026-07-25 follow-up verification

- Inspected all six Gag Shop exterior BAMs with Panda3D. Five resolve the
  `phase_3.5/maps/GS_sign.png` slot and the Bossbot-area variant resolves
  `phase_8/maps/GS_signBIG_BR.png`.
- Both replacement sign files are transparent 256×256 RGBA images with
  SHA-256
  `A29CE47E001670A52868C60545DA23476A8C786A752D49B07B5F66B39E1DEA23`.
- The English localizer resolves the player-visible shop title to `Gag Shop`.
- Offscreen avatar-chooser renders passed at 1920×1080 and 1024×768, including
  the aspect-aware background, neutral side fill, and Exit label.
- The Options page exposes distinct Advanced Settings, Main Menu, and Exit
  callbacks; Main Menu follows the normal chooser flow and Exit uses its own
  confirmation.
- All seven focused keyboard-shortcut tests passed. A headless ShowBase import
  check loaded Avatar, OTPDialog, and AvatarChooser without a circular import.
- The expanded shortcut suite passed all 11 tests, including Caps Lock toggle,
  foreground text-entry protection, background-chat handling, safe
  unregistration, dialog priority, and Space/Escape routing.
- The offscreen quest-overlay verifier constructed all four quest slots, opened
  and closed the overlay with Caps Lock, closed it with Escape, and completed
  teardown without an exception. It used Stinky's real completed quest
  descriptor and asserted that every poster belongs to the overlay and renders
  above its backdrop.
- A live client test as Stinky in Moonlight Meadows confirmed that the normal
  hidden/background SpeedChat focus does not consume Caps Lock, the completed
  ToonTask card is readable, Caps Lock toggles the view closed, and Escape
  closes it without opening a lower-priority menu.
- The focused XP verifier returned 10× for a street battle, 40× with invasion
  and More-XP, 13× for a three-story building, 52× for that building with both
  global bonuses, and 80× for the tested third Cogdo floor with both bonuses.
  Its wiring audit confirmed each multiplier is applied once.
- The complete Astron database was backed up before changing Stinky. The
  avatar was then verified at 137/137 Laff with every gag track maxed, an
  80-capacity max inventory, and all 13 supported hood visits and teleports.
- The first live Stinky login exposed missing two-byte Astron length prefixes
  on the edited experience and inventory blobs. With all services stopped,
  both fields were repaired; the game's `Experience` and `InventoryBase`
  decoders then passed, Astron accepted the object, and a live login completed.
- Astron, UberDOG, and the AI district restarted successfully after the save
  change, and TCP ports 7198 and 7199 returned to listening on loopback.
- Live at 1920x1080, the chooser showed a centered background, neutral side
  fill, the Stinky card, and Exit. From Options, Escape safely canceled both
  Main Menu and Exit confirmations, dismissed the Shticker Book and Advanced
  Settings, and acknowledged a one-button quest notice.
- Confirming Main Menu returned from Central Commons to the chooser. Selecting
  Stinky again returned to a playable Central Commons at 137/137 Laff.
- The live Advanced Settings page showed the 60 FPS cap plus FPS meter, VSync,
  MSAA, texture filtering, independent volume, particles, and FOV controls.
- The running client's log contained no targeted traceback, fatal, short-read,
  eject, assertion, or exception pattern after the repaired login, Main Menu
  round-trip, and final Caps Lock overlay test.
- The final regression pass reparsed all 1,849 Python files, passed all 11
  keyboard tests, passed the quest-overlay and gag-XP verifiers, passed both
  launcher `--check` paths, and found no whitespace errors in either nested Git
  worktree.

## 2026-07-26 P0 source verification

The first P0 implementation pass produced the following focused results:

- `game\tools\test_minigame_skip.py` passed all 18 tests. Coverage includes
  active-play state gating, solo and unanimous group votes, duplicate and
  outsider rejection, visible vote updates, explicit-skip zero-reward wiring,
  normal-completion-only ToonTask credit, once-only credit, child-game state
  gating, ineligible-state UI teardown, known cleanup guards, source parsing,
  and the distributed-class field.
- `game\tools\test_fishing_server.py` passed all 11 tests. Coverage includes
  quest-item precedence, fish collection/tank writes, invalid-fish fallback,
  rod-specific jellybean catches, full-tank rejection, tank sale/trophy
  behavior, unique pier claims, requested-fish rod validation, one-time cast
  charging, invalid cast rejection, and target distance/flight-time checks.
- `game\tools\test_fishing_persistence.py` passed all 10 tests. Coverage includes
  tank removal and bounds, tank/collection network round trips, collection
  records, all five fishing reconnect payload fields, client boot paths, and
  the retained persistent DC declarations. Its pond-plane regression confirms
  that a target's below-surface Z offset cannot invalidate an otherwise valid
  X/Y hit.
- `game\tools\test_diving_twod_cleanup.py` passed all 8 tests covering
  collision, mask, control, Laff-meter, task, event, and Ring ending-task
  cleanup.
- `game\tools\test_race_cleanup.py` passed all 5 tests covering owned tasks,
  intervals, dice state, avatar neutralization, and idempotent early teardown.
- `game\tools\test_target_photo_cleanup.py` passed all 12 tests covering
  delayed work, intervals, collision state, and barriers.
- `game\tools\test_live_minigame_harness.py` passed all 7 tests, and PowerShell
  parsing accepted `game\tools\start_live_minigame_clients.ps1`.
- Panda3D's DC parser accepted `game\etc\toon.dc` after the skip-vote field was
  added.
- The earlier pre-harness pass AST-parsed all 1,854 game-worktree Python files
  then present, and `git diff --check` found no whitespace errors.
- A real AI server startup running the changed source reached
  `ToontownAIRepository: Done.`

This verification includes focused automation and server startup plus the live
public-hood fishing, solo Maze, and two-player Maze results below. It does not
claim a four-player unanimous vote or an all-minigame lifecycle sweep.
Estate-pond fishing and Fish Bingo remain open.

### Live public-hood fishing catch, persistence, and sale

- A fresh local client made an authoritative cast at the Central Commons
  public pond and caught a Party Clown Fish: genus `4`, species `2`, weight
  `40`, value `6`.
- The accepted cast changed money from `39` to `38`, collection size from `0`
  to `1`, and tank size from `0` to `1`.
- After a clean disconnect, the avatar YAML stored money `38`, collection `1`,
  and tank `1`.
- Reconnecting rehydrated collection `1`, tank `1`, and tank value `6`.
- The live Fisherman Freddy flow sold the fish. The tank changed from `1` to
  `0`, while money changed from `38` to the wallet cap of `40`.
- Post-sale YAML retained collection `1`, stored tank `0`, and stored money
  `40`. A final reconnect reproduced collection `1`, tank `0`, and money `40`.

This verifies the ordinary public-hood catch, persistence, fisherman sale, and
post-sale reconnect path. It does not validate estate ponds, Fish Bingo, or a
multiplayer fishing session.

### Live solo Maze skip

- The common skip button was visible during active Maze gameplay and absent
  from the rules screen.
- The explicit confirmation stated that every player must agree.
- The solo Yes vote produced Astron events for `minigame_skip_vote` (`1|1`),
  `minigame_skipped`, and a normal `minigame` purchase transition with reward
  `0`.
- The client reached the Gag Shop, returned to Central Commons, and its fresh
  log contained no targeted traceback, assertion, task-error, fatal, or
  exception-exit pattern.

This confirms the one-player Maze path. The four-player vote path and
every-game leak/cleanup sweep remain open.

Before that clean run, reusing the developer-only `~mg maze` teleport in a
client that had already completed Maze triggered a PandaNode render assertion.
The fresh-client skip run did not reproduce it. The repeat-teleport behavior
remains an open test-harness issue in `changes\TODO.md`; the repeatable launcher
below avoids it by starting fresh client processes.

### Repeatable live-client harness

- `game\tools\start_live_minigame_clients.ps1` starts one through four clients
  with distinct local account tokens, fixed tiled windows, and separate
  persistent logs.
- `game\tools\live_minigame_client.py` loads the game source path, reapplies
  test-window properties after saved settings load, dismisses blocking login
  quest popups, requests the selected minigame from the first client, and
  boards every client onto the same trolley.
- The helper redirects all four Python output streams to stable files so the
  clients remain usable after the starting PowerShell process exits.

### Live two-player Maze skip

- Two fresh clients selected Stinky (`100000001`) and Deputy Moe Crumblehoffer
  (`100000003`); both joined Maze Game `6` in zone `2000`.
- Both clients displayed `Skip votes: 1/2` after the first vote, and the game
  remained active.
- Astron then recorded the second vote as `2/2`, followed by
  `minigame_skipped`.
- Astron emitted one `minigame` result for each avatar with reward `0`.
- Both clients completed the Gag Shop purchase transition and returned to
  Central Commons. Escape dismissed each post-return quest popup.
- Neither fresh client log contained a targeted traceback, assertion,
  task-error, fatal, or exception-exit match.

This confirms the two-player Maze path. Four-player voting and the full
one-, two-, and four-player lifecycle matrix remain open.

## Platform boundary

The Windows runtime, server lifecycle, launcher checks, and headless game
checks passed. The macOS/Linux launcher and native start/build scripts were not
executed on their target operating systems. A working non-Windows game stack
still requires an ABI-matched custom Panda3D build with the OTP/Toontown
extensions and a target-native Astron build; Linux Astron is not included.
