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
  - Evaluate client target hits on the pond's X/Y plane so target depth does
    not turn a valid cast into a visual miss.
  - Add persistence and reconnect tests before enabling Fish Bingo.
  - Source, focused tests, DC parsing, AI startup, and a live client
    catch/sale/reconnect cycle passed on 2026-07-26.
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
  - [x] Catch and sell fish in a public hood pond, reconnect, and confirm
    persisted collection/tank state.
    - A Party Clown Fish catch persisted through disconnect and reconnect with
      collection `1`, tank `1`, and value `6`.
    - The live Fisherman Freddy sale emptied the tank, retained the collection,
      and persisted the capped wallet value of `40` through another reconnect.
  - [x] Exercise a solo skip from active gameplay.
    - A live Maze Game skip produced unanimous `1/1` vote, skip, and
      zero-reward server events, then returned cleanly to Central Commons.
  - [x] Exercise a two-player unanimous skip and visible vote status.
    - Both clients displayed `Skip votes: 1/2` after the first vote.
    - Astron recorded the second vote as `2/2`, the unanimous skip, and a
      zero-reward result for each avatar.
    - Both clients returned cleanly to Central Commons, and Escape dismissed
      their post-return quest popups.
  - [ ] Repeat the unanimous skip with four players.

## P1 - Minigame correctness and testing

- [x] Preserve every Photo Fun score from the final shutter before processing
  the client's film-out notification.
- [x] Correct Toon Escape AI's mismatched initialization-guard attribute.
- [x] Remove unreachable Trolley Tracks place-decider branches containing
  `TODO NAME` and unqualified localizer symbols.
- [ ] Build a server-GUI **Force Next Minigame** selector.
- [ ] Complete the repeatable test harness for minigame IDs 1 through 16.
  - [x] Launch fresh one-, two-, three-, or four-player client groups with
    distinct accounts, windows, and persistent logs.
  - [x] Select an arbitrary minigame ID/name from the first client and board
    every client on the same trolley.
  - [ ] Automate normal completion, gameplay skip, disconnect, and early-exit
    cleanup scenarios.
  - [ ] Record and assert jellybean rewards, ToonTask credit, and leaked
    tasks, intervals, distributed objects, or barriers.
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
- [ ] Add and validate a separate voluntary exit/skip policy for Cogdo
  activities; retain their existing disconnect/barrier cleanup.
- [ ] Define active-game exit policy and live-validate the existing
  picnic-table request-exit cleanup.
- [ ] Define active-game exit policy and live-validate the existing kart
  racing and golf leave/disconnect paths.
- [ ] Define consistent exit policy and live-validate the existing party
  activity and estate-cannon cleanup paths.
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

- [ ] Finish a reproducible, distributable macOS custom Panda3D runtime.
  - [x] Build and smoke-test a local Apple Silicon CPython 3.9.25/Panda3D
    1.11.0 runtime with `panda3d.otp` and `panda3d.toontown`.
  - [ ] Document the exact custom-Panda source revision and build recipe.
  - [ ] Remove absolute Homebrew linkage and verify on a clean Mac.
- [ ] Finish the native macOS Astron and launcher distribution.
  - [x] Build and run a local arm64 Astron server with the complete
    Astron/UberDOG/AI/client stack.
  - [x] Pass source-launcher runtime validation and a live client
    login/world-entry/normal-exit smoke test.
  - [ ] Remove absolute Homebrew `yaml-cpp`/`libuv` linkage.
  - [ ] Build, sign, notarize, and clean-machine test the launcher `.app`.
- [ ] Build ABI-matched custom Panda3D and Astron stacks for Linux.
- [ ] Add Windows, macOS, and Linux CI jobs for parsing, focused tests, and
  launcher validation.
- [ ] Package versioned releases without logs, caches, live databases, player
  backups, or the development runtime.
  - [x] Exclude those paths from the source archive through tracked ignore and
    publication rules.
  - [ ] Add version tags, a release workflow, manifests, checksums, and
    reproducible package validation.
- [ ] Add first-run configuration, runtime validation, and actionable launcher
  error messages for every supported platform.
  - [x] Download/validate pinned resources, validate custom Panda imports,
    detect native Astron, and build/verify the neutral overlay during setup.
  - [ ] Persist Unix runtime selection and validate CPU architecture plus
    dynamic-library dependencies.
  - [ ] Validate Astron readiness and resource completeness from the launcher.
  - [ ] Run clean-machine first-launch tests on all three platforms.

## P2 - Public-release readiness

- [ ] Choose the final project name and perform a deliberate repo-wide rename.
- [ ] Replace or separately source every retained upstream asset before
  describing a public release as independently rights-cleared.
- [ ] Complete governance and attribution documentation.
  - [x] Add Open Town/upstream licenses, third-party notices, and contribution
    guidance.
  - [ ] Add standalone `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
    `SECURITY.md`, and asset-attribution/provenance files.
- [ ] Document clean-room asset provenance and redistribution permissions.
- [ ] Remove development authentication defaults from production builds.
- [ ] Add server-side rate limits and per-action budgets for client-authored
  gameplay RPCs before public deployment.
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
- [x] Add the ordinary public-hood fishing AI/server source path and 21 focused
  server/persistence tests.
- [x] Live-validate an authoritative public-hood fish catch, persistence
  reconnect, Fisherman Freddy sale, and post-sale reconnect.
- [x] Add active-play-only, confirmed, unanimous minigame skipping with 18
  focused tests.
- [x] Require normal non-skipped completion for play-minigame ToonTask credit.
- [x] Add focused early-exit cleanup coverage for Diving, TwoD, Ring, Race,
  Target, and Photo Game.
- [x] Add a repeatable fresh-client live minigame launcher with distinct
  accounts, per-client logs, deterministic Maze selection, popup dismissal,
  and tiled one- through four-client windows.
- [x] Live-validate a two-player unanimous Maze skip with visible vote status,
  zero rewards, and clean playground returns.

## Maintenance rule

When an item changes:

1. Update its checkbox and wording here.
2. Record the exact files and behavior in the dated Markdown change log.
3. Add or update an automated verification where practical.
4. Update `VERIFICATION.md` with the observed result.
5. Regenerate the local-only `FULL_FILE_INDEX.txt` if it is present and files
   were added or removed. It is intentionally excluded from the public
   repository because it inventories private runtime and database paths.
