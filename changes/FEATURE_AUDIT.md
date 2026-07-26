# Gameplay feature audit

This audit records what is actually present in the local Open Town fork
through 2026-07-26. Source presence is not treated as proof that a feature
completes successfully in a live multiplayer session.

## Caps Lock quest view

The Caps Lock quest view is implemented.

- Caps Lock toggles a dedicated overlay without moving or corrupting the
  Shticker Book's Quest page.
- Escape closes the overlay.
- The overlay is registered for the lifetime of the local Toon, rather than
  only while walking in a playground, so it remains available in interiors,
  battles, activities, minigames, fishing states, and transitions.
- It uses the same `QuestBookPoster` renderer as the Shticker Book and displays
  every active ToonTask up to the game's four-task carry limit.
- Quest descriptions, progress, completion state, NPC destinations, and map
  number badges update when the avatar's quest data changes.
- A foreground chat, name, code, or password entry retains Caps Lock instead
  of opening the overlay. The normal background-focus chat entry does not
  block it during gameplay.

The current quest database contains 1,469 configured quest IDs across 31 quest
types. Those types already share the poster renderer used by the new overlay.

## Fishing

The authoritative ordinary public-hood fishing source path is implemented.
It has focused server/persistence coverage and reached normal AI startup, but a
live client catch, sale, and reconnect have not yet been recorded.

Implemented:

- 70 fish species, five rods, 24 pond-zone tables, and the existing client
  aiming, casting, catch, bucket, tutorial, and selling interfaces.
- Recursive public-hood pond-DNA pier generation and configured moving target
  generation.
- Authoritative pier occupancy and rejection of second-pier, wrong-zone,
  invalid-rod, insufficient-jellybean, full-tank, duplicate-cast, and invalid
  cast-parameter requests.
- One cast charge per accepted cast, a pending-cast requirement, and
  server-side target distance/flight-time validation.
- Quest-item, fish, jellybean, and boot catch outcomes, including rod checks
  for requested fish.
- Persistent fish collection and tank writes, collection record results,
  fisherman tank sales, tank clearing, fishing trophies, and trophy Laff.
- Safe indexed tank removal, client boot-label handling, Bingo-boot last-catch
  routing, and nonnegative client target-movement duration.
- Existing avatar persistence fields for fish collection, tank capacity,
  tank contents, rod, and trophies retain their wire contract.

Focused checks:

- 11 authoritative fishing-server tests passed.
- 9 tank, collection, reconnect-payload, client-contract, and DC-contract
  tests passed.
- The DC schema parsed successfully.
- The AI process running the changed source reached
  `ToontownAIRepository: Done.`

Remaining boundaries:

- A live client catch, sale, and reconnect/persistence walkthrough is still
  required.
- Estate-pond fishing is outside this public-hood implementation and remains
  unfinished.
- Fish Bingo still has no authoritative server gameplay.

## Trolley minigames

The repository has client, AI, and network declarations for all 16 standard
trolley minigames plus the optional Trolley Tracks metagame:

1. Race Game
2. Cannon Game
3. Tag Game
4. Match the Dance Coach
5. Ring Game
6. Maze Game
7. Tug-of-War
8. Catching Game
9. Treasure Dive
10. Toon Slingshot
11. Toon Memory Game
12. Jungle Vines
13. Ice Slide
14. Cog Thief
15. Toon Escape
16. Photo Fun
17. Trolley Tracks, used only by its optional metagame flow

All 132 files under `toontown/minigame` parsed across the full-tree and
changed-source passes. This confirms source integrity, not full live
completion. There is no permanent per-game regression suite, and all 16 have
not been completed live on this fork.

Notable selection behavior:

- Solo players have 11 historically eligible games.
- `want-all-minigames` currently defaults to true, so groups of two or more
  can draw from all 16 standard games instead of the historical player-count
  matrix.
- Trolley Tracks remains outside ordinary random selection.

### Can trolley minigames be skipped?

Yes. The common skip path now has an explicit lifecycle and multiplayer
policy.

- The bottom-right Skip Minigame button is inherited by all 16 standard
  trolley games and Trolley Tracks, but appears only during active
  `frameworkGame` play.
- Selecting it opens an explicit Yes/No confirmation.
- Every unique current participant must vote; the client shows the current
  vote count/status.
- The server rejects nonparticipants and ignores duplicate votes.
- A completed unanimous skip gives every participant zero jellybeans.
- Play-minigame ToonTask credit is granted once for normal, non-skipped
  completion before the client-exit barrier. A skip does not count.
- Known early-abort cleanup fields in Toon Escape, Maze Game, and Treasure
  Dive are guarded.
- The policy and wiring passed 17 focused tests, including solo/group voting,
  duplicates, outsiders, early states, quest credit, cleanup guards, and DC
  parsing.
- A live solo Maze run showed the button only during active gameplay, recorded
  the unanimous `1/1` vote and skip events, awarded zero jellybeans, and
  returned cleanly to the playground.

The common skip does **not** cover Cogdo activities, picnic-table games, kart
racing, golf, fishing, party activities, or estate cannons because those
systems use different base classes and lifecycle rules.

Still unverified:

- A live multi-client unanimous vote and visible status update.
- Normal completion, skip, disconnect, and cleanup in live one-, two-, and
  four-player runs of every standard trolley game and Trolley Tracks.
- Absence of leaked tasks, intervals, distributed objects, and barriers across
  that full live matrix.

Confirmed minigame defects found by the audit:

- Photo Fun discards the last photograph because it increments the film count
  and returns before recording that final score.
- Toon Escape checks and sets two differently spelled initialization guards.
- Dormant Trolley Tracks result branches retain an unqualified symbol and
  `TODO NAME` text.
- Early cleanup is not uniformly idempotent.

## Prioritized remaining work

1. Live-test a public-hood fish catch, sale, and reconnect/persistence cycle.
2. Live-test unanimous minigame skipping and the full one-, two-, and
   four-player cleanup matrix.
3. Implement estate-pond fishing and then authoritative Fish Bingo.
4. Repair Photo Fun's final-film score ordering and Toon Escape's guard typo.
5. Add a forced-minigame test harness for IDs 1 through 16 at one, two, and
   four players, including skip timing and cleanup assertions.
6. Add separate, lifecycle-aware skip or exit policies for Cogdo, party,
   racing, golf, picnic-table, and estate activities if universal skipping is
   desired.
7. Localize the remaining hardcoded minigame result text.
8. Add a server-GUI force-next-minigame selector and a per-game validation
    checklist.
9. Build and test native macOS and Linux Panda3D/Astron stacks; the supplied
    launch scripts alone do not make the Windows native game runtime portable.
10. Replace or separately source every retained upstream asset before any
    claim that a public release is independently rights-cleared.
