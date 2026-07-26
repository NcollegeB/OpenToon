# Project to-do list

This is the living implementation backlog for Open Town. Check an item only
after its acceptance criteria have passed and the result is recorded in
`2026-07-25.md` or a newer dated change log.

## P0 - Playable core systems

- [x] Implement ordinary public-hood fishing on the AI/server.
  - Generate distributed fishing spots from pond DNA.
  - Implement authoritative target generation, cast validation, catch rolls,
    jellybean costs, fish records, trophies, and quest progress.
  - Implement selling and tank clearing through a real `FishManagerAI`.
  - Repair `FishTank.removeFishAtIndex()` and its undefined variable.
  - Add persistence and reconnect tests before enabling Fish Bingo.
  - Source, focused tests, DC parsing, and AI startup passed on 2026-07-26;
    live client catch/sale/reconnect validation remains open separately below.
- [ ] Make trolley-minigame skipping lifecycle-safe.
  - [x] Restrict skipping to active gameplay.
  - [x] Guard known early-abort cleanup fields in Toon Escape, Maze Game, and
    Treasure Dive.
  - [ ] Confirm every game exits without leaked tasks, intervals, distributed
    objects, or barriers in live one-, two-, and four-player runs.
- [x] Choose and implement a multiplayer skip policy.
  - Use a unanimous vote from every unique current participant.
  - Add an explicit confirmation and visible vote/status UI.
  - Keep zero jellybean rewards for a fully skipped game.
- [x] Make skipped minigames ineligible for ToonTask completion credit.
  - Move quest credit from game creation to normal `gameOver()` before the
    client-exit barrier.
  - Add server tests for completed, skipped, and duplicate-credit cases.
- [ ] Complete live validation for the new P0 paths.
  - Catch and sell fish in a public hood pond, reconnect, and confirm persisted
    collection/tank state.
  - [x] Exercise a solo skip from active gameplay.
    - A live Maze Game skip produced unanimous `1/1` vote, skip, and
      zero-reward server events, then returned cleanly to Central Commons.
  - Exercise a two- or four-player unanimous skip and visible vote status.

## P1 - Minigame correctness and testing

- [ ] Repair Photo Fun so the final photograph is scored before film runs out.
- [ ] Correct Toon Escape's mismatched initialization-guard spelling.
- [ ] Remove the dormant Trolley Tracks `TODO NAME` and unqualified-symbol
  branches.
- [ ] Build a server-GUI **Force Next Minigame** selector.
- [ ] Add a repeatable test harness for minigame IDs 1 through 16.
  - Exercise one-, two-, and four-player configurations.
  - Test normal completion, gameplay skip, disconnect, and early-exit cleanup.
  - Record jellybean rewards and ToonTask credit.
  - Investigate the PandaNode assertion seen when the developer-only `~mg`
    teleport was reused in an already-running client before relying on it for
    batch live sweeps.
- [ ] Complete one live validation checklist for every standard trolley game
  and Trolley Tracks.
- [ ] Localize the remaining hardcoded minigame-result text.

## P1 - Activity coverage

- [ ] Implement estate-pond fishing generation and its estate-specific flow.
- [ ] Implement authoritative Fish Bingo only after ordinary fishing passes
  live persistence and multiplayer validation.
- [ ] Design separate, lifecycle-aware exit or skip behavior for Cogdo
  activities.
- [ ] Design exit or skip behavior for picnic-table games.
- [ ] Design exit or skip behavior for kart racing and golf.
- [ ] Design exit or skip behavior for party activities and estate cannons.
- [ ] Live-validate ordinary fishing pier exit and disconnect cleanup.

## P2 - Quest-view polish

- [ ] Add an optional configurable key binding for the quest overlay.
- [ ] Add an Options toggle for completed-task highlighting and map-number
  badges.
- [ ] Test the overlay live during a battle, interior, trolley game, fishing
  state, teleport transition, and four-active-quest profile.
- [ ] Add controller-accessible open/close input if controller support is
  enabled.

## P2 - Platform and release engineering

- [ ] Build ABI-matched custom Panda3D OTP/Toontown runtimes for macOS.
- [ ] Build a native macOS Astron server and test the complete launcher flow.
- [ ] Build ABI-matched custom Panda3D and Astron stacks for Linux.
- [ ] Add Windows, macOS, and Linux CI jobs for parsing, focused tests, and
  launcher validation.
- [ ] Package versioned releases without logs, caches, live databases, player
  backups, or the development runtime.
- [ ] Add first-run configuration, runtime validation, and actionable launcher
  error messages for every supported platform.

## P2 - Public-release readiness

- [ ] Choose the final project name and perform a deliberate repo-wide rename.
- [ ] Replace or separately source every retained upstream asset before
  describing a public release as independently rights-cleared.
- [ ] Add license, contributor, code-of-conduct, security, and attribution
  files.
- [ ] Document clean-room asset provenance and redistribution permissions.
- [ ] Remove development authentication defaults from production builds.
- [ ] Add account security, moderation, backup, restore, and database-migration
  plans before accepting public players.

## Completed in the current local build

- [x] Add a global Caps Lock current-ToonTasks overlay.
- [x] Display every active quest slot through the shared quest-poster renderer.
- [x] Close the quest overlay with Caps Lock or Escape.
- [x] Preserve foreground text-entry handling and allow normal background
  SpeedChat focus.
- [x] Add 11 focused keyboard-routing tests and an offscreen quest-overlay
  verifier.
- [x] Audit fishing implementation status.
- [x] Audit all 16 standard trolley minigames and Trolley Tracks.
- [x] Document minigame-skip coverage, limitations, and confirmed defects.
- [x] Add the ordinary public-hood fishing AI/server source path and 20 focused
  server/persistence tests.
- [x] Add active-play-only, confirmed, unanimous minigame skipping with 17
  focused tests.
- [x] Require normal non-skipped completion for play-minigame ToonTask credit.

## Maintenance rule

When an item changes:

1. Update its checkbox and wording here.
2. Record the exact files and behavior in the dated Markdown change log.
3. Add or update an automated verification where practical.
4. Update `VERIFICATION.md` with the observed result.
5. Regenerate `FULL_FILE_INDEX.txt` if files were added or removed.
