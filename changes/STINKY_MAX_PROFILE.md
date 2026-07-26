# Stinky max-profile record

Date: 2026-07-25

This was an explicitly requested local save change for testing every area and
gag track.

## Avatar identity

- Avatar name: `Stinky`
- Avatar object ID: `100000001`
- Account object ID: `100000000`
- Name and object IDs were preserved.

## Safety and recovery

All client/server services were stopped before the YAML database was copied or
edited.

Pre-change full database backup:

```text
backups/stinky-max-20260725-134349/astrondb
```

Pre-change Stinky YAML SHA-256:

```text
04980981C662A48DC0A00AAB9194816495FA4D9392F7CC914C76074337097CED
```

Post-change Stinky YAML SHA-256:

```text
FF19C76D92551691B6F4AFBB460F7933716B46282AA0445E08ADFBA24ABA4B1E
```

To restore this snapshot, stop all three services first, copy the backed-up
`astrondb` directory back to `game/astron/databases/astrondb`, and then start
the services again.

## Requested fields changed

- `setMaxHp`: 137
- `setHp`: 137
- `setMaxCarry`: 80
- `setTrackAccess`: all seven gag tracks unlocked
- `setExperience`: 10,000 XP for each of the seven tracks
- `setInventory`: the exact inventory produced by the game's `maxOutInv()`
  logic
- Regular gag inventory: 73 regular gags at the normal per-gag carry caps
- Level-seven inventory: one level-seven gag in each track
- `setHoodsVisited`: all 13 hoods supported by `HoodsForTeleportAll`
- `setTeleportAccess`: the same 13 supported hood IDs

Teleport/visited hood IDs:

```text
1000, 2000, 3000, 4000, 5000, 6000, 8000,
9000, 10000, 11000, 12000, 13000, 17000
```

Unrequested progression such as quests, suits, fishing, gardening, golf,
karting, jellybeans, and trophies was left unchanged.

## Verification

- The first live login correctly exposed that the updated variable-length
  blobs were missing Astron's two-byte little-endian length prefixes. The
  services were stopped again and both fields were repaired before testing
  continued.
- `setExperience` now has a `0e00` prefix for its 14-byte payload and decodes
  through the game's `Experience` class to seven values of 10,000.
- `setInventory` now has a `3100` prefix for its 49-byte payload and decodes
  through the game's `InventoryBase` class to 80 total gags: 73 regular gags
  plus one level-seven gag in every track.
- Astron, UberDOG, and the AI district restarted with new healthy processes.
- TCP 7198 and 7199 returned to listening on `127.0.0.1`.
- The new Astron event log shows normal AI world/building generation.
- A live Windows login as Stinky completed after the repair. The on-screen
  Laff meter showed 137/137, the Main Menu round-trip returned to the avatar
  chooser, and selecting Stinky again returned to a playable Central Commons.
