# Intentional File Inventory

This is the GitHub publishing inventory for the customized local bundle. All paths are relative to `Open-Toontown-Local/`.

Status key:

- **M** — modified file already tracked by its Git repository.
- **A** — intentional new authored file not yet tracked.
- **B** — intentional bundle, launcher, or documentation file outside the nested Git repositories.
- **G** — generated distributable; publish as a release artifact if desired, not as source.

The `game/` and `game/resources/` sections reflect the intentional status
snapshots through 2026-07-26. An untracked directory is expanded below into
its intentional authored files so caches are not accidentally included.

## Game code, configuration, scripts, and tests

### Modified tracked files

- **M** `game/PPYTHON_PATH`
- **M** `game/astron/config/astrond.yml`
- **M** `game/darwin/start-ai-server.sh`
- **M** `game/darwin/start-astron-server.sh`
- **M** `game/darwin/start-game.sh`
- **M** `game/darwin/start-uberdog-server.sh`
- **M** `game/etc/Configrc.prc`
- **M** `game/etc/toon.dc`
- **M** `game/linux/start-ai-server.sh`
- **M** `game/linux/start-astron-server.sh`
- **M** `game/linux/start-game.sh`
- **M** `game/linux/start-uberdog-server.sh`
- **M** `game/otp/avatar/Avatar.py`
- **M** `game/otp/avatar/DistributedPlayerAI.py`
- **M** `game/otp/friends/FriendSecret.py`
- **M** `game/otp/login/AstronLoginManagerUD.py`
- **M** `game/otp/otpbase/OTPLocalizerEnglish.py`
- **M** `game/otp/otpgui/OTPDialog.py`
- **M** `game/toontown/ai/AIStart.py`
- **M** `game/toontown/ai/ToontownAIRepository.py`
- **M** `game/toontown/battle/BattleCalculatorAI.py`
- **M** `game/toontown/battle/DistributedBattleBaseAI.py`
- **M** `game/toontown/battle/MovieToonVictory.py`
- **M** `game/toontown/building/DistributedSuitInterior.py`
- **M** `game/toontown/building/DistributedSuitInteriorAI.py`
- **M** `game/toontown/building/DistributedTutorialInterior.py`
- **M** `game/toontown/catalog/CatalogFurnitureItem.py`
- **M** `game/toontown/catalog/CatalogScreen.py`
- **M** `game/toontown/cogdominium/DistCogdoGame.py`
- **M** `game/toontown/cogdominium/DistributedCogdoInteriorAI.py`
- **M** `game/toontown/coghq/DistributedBanquetTable.py`
- **M** `game/toontown/coghq/DistributedCashbotBossCrane.py`
- **M** `game/toontown/coghq/DistributedGolfSpot.py`
- **M** `game/toontown/effects/Firework.py`
- **M** `game/toontown/effects/FireworkGlobals.py`
- **M** `game/toontown/effects/FireworkShow.py`
- **M** `game/toontown/estate/GardenGlobals.py`
- **M** `game/toontown/fishing/BingoCardCell.py`
- **M** `game/toontown/fishing/BingoGlobals.py`
- **M** `game/toontown/fishing/DistributedFishingPond.py`
- **M** `game/toontown/fishing/DistributedFishingPondAI.py`
- **M** `game/toontown/fishing/DistributedFishingTarget.py`
- **M** `game/toontown/fishing/DistributedFishingTargetAI.py`
- **M** `game/toontown/fishing/FishTank.py`
- **M** `game/toontown/friends/FriendsListPanel.py`
- **M** `game/toontown/hood/BRHoodDataAI.py`
- **M** `game/toontown/hood/DDHoodDataAI.py`
- **M** `game/toontown/hood/DGHoodDataAI.py`
- **M** `game/toontown/hood/DLHoodDataAI.py`
- **M** `game/toontown/hood/GSHoodDataAI.py`
- **M** `game/toontown/hood/GZHoodDataAI.py`
- **M** `game/toontown/hood/MMHoodDataAI.py`
- **M** `game/toontown/hood/OZHoodDataAI.py`
- **M** `game/toontown/hood/TTHoodDataAI.py`
- **M** `game/toontown/login/AvatarChooser.py`
- **M** `game/toontown/minigame/DistributedDivingGame.py`
- **M** `game/toontown/minigame/DistributedDivingGameAI.py`
- **M** `game/toontown/minigame/DistributedMazeGame.py`
- **M** `game/toontown/minigame/DistributedMazeGameAI.py`
- **M** `game/toontown/minigame/DistributedMinigame.py`
- **M** `game/toontown/minigame/DistributedMinigameAI.py`
- **M** `game/toontown/minigame/DistributedPatternGame.py`
- **M** `game/toontown/minigame/DistributedPhotoGame.py`
- **M** `game/toontown/minigame/DistributedRaceGame.py`
- **M** `game/toontown/minigame/DistributedRingGame.py`
- **M** `game/toontown/minigame/DistributedTargetGame.py`
- **M** `game/toontown/minigame/DistributedTargetGameAI.py`
- **M** `game/toontown/minigame/DistributedTwoDGame.py`
- **M** `game/toontown/minigame/DistributedTwoDGameAI.py`
- **M** `game/toontown/minigame/MinigameCreatorAI.py`
- **M** `game/toontown/parties/PartyCogActivityInput.py`
- **M** `game/toontown/quest/QuestParser.py`
- **M** `game/toontown/safezone/DistributedFishingSpot.py`
- **M** `game/toontown/safezone/DistributedFishingSpotAI.py`
- **M** `game/toontown/safezone/PublicWalk.py`
- **M** `game/toontown/shtiker/DisplaySettingsDialog.py`
- **M** `game/toontown/shtiker/OptionsPage.py`
- **M** `game/toontown/shtiker/ShtikerBook.py`
- **M** `game/toontown/shtiker/SummonCogDialog.py`
- **M** `game/toontown/toon/InventoryNew.py`
- **M** `game/toontown/toon/LocalToon.py`
- **M** `game/toontown/toon/PlayerInfoPanel.py`
- **M** `game/toontown/toonbase/DisplayOptions.py`
- **M** `game/toontown/toonbase/TTLocalizerEnglish.py`
- **M** `game/toontown/toonbase/ToonBase.py`
- **M** `game/toontown/toonbase/ToontownBattleGlobals.py`
- **M** `game/toontown/toontowngui/NewsPageButtonManager.py`
- **M** `game/toontown/town/TownBattle.py`
- **M** `game/toontown/town/TownBattleSOSPanel.py`
- **M** `game/toontown/tutorial/TutorialManager.py`
- **M** `game/toontown/uberdog/UDStart.py`
- **M** `game/win32/start_ai_server.bat`
- **M** `game/win32/start_astron_server.bat`
- **M** `game/win32/start_game.bat`
- **M** `game/win32/start_uberdog_server.bat`

### New authored files

- **A** `game/otp/otpbase/NeutralBranding.py`
- **A** `game/otp/otpgui/KeyboardShortcutManager.py`
- **A** `game/toontown/ai/FishManagerAI.py`
- **A** `game/toontown/minigame/MinigameSkipPolicy.py`
- **A** `game/tools/live_minigame_client.py`
- **A** `game/tools/platform_runtime.sh`
- **A** `game/tools/SERVER_GUI.md`
- **A** `game/tools/server_gui.py`
- **A** `game/tools/start_live_minigame_clients.ps1`
- **A** `game/tools/test_diving_twod_cleanup.py`
- **A** `game/tools/test_fishing_persistence.py`
- **A** `game/tools/test_fishing_server.py`
- **A** `game/tools/test_keyboard_shortcuts.py`
- **A** `game/tools/test_live_minigame_harness.py`
- **A** `game/tools/test_minigame_skip.py`
- **A** `game/tools/test_race_cleanup.py`
- **A** `game/tools/test_target_photo_cleanup.py`
- **A** `game/tools/verify_gag_xp.py`
- **A** `game/tools/verify_gagshop_models.py`
- **A** `game/tools/verify_quest_overlay.py`
- **A** `game/toontown/quest/QuestOverlay.py`
- **A** `game/toontown/shtiker/GraphicsOptionsDialog.py`
- **A** `game/win32/start_server_gui.bat`

## Resource repository

### Modified tracked resources

- **M** `game/resources/phase_3.5/dna/storage_tutorial.dna`
- **M** `game/resources/phase_3.5/dna/tutorial_street.dna`
- **M** `game/resources/phase_3.5/maps/GS_sign.png`
- **M** `game/resources/phase_3/etc/QuestScripts.txt`
- **M** `game/resources/phase_4/dna/storage.dna`
- **M** `game/resources/phase_4/dna/toontown_central_sz.dna`
- **M** `game/resources/phase_4/maps/daisys_garden_5100_english.png`
- **M** `game/resources/phase_4/maps/daisys_garden_5200_english.png`
- **M** `game/resources/phase_4/maps/daisys_garden_5300_english.png`
- **M** `game/resources/phase_4/maps/donalds_dock_1100_english.png`
- **M** `game/resources/phase_4/maps/donalds_dock_1200_english.png`
- **M** `game/resources/phase_4/maps/donalds_dock_1300_english.png`
- **M** `game/resources/phase_4/maps/donalds_dreamland_9100_english.png`
- **M** `game/resources/phase_4/maps/donalds_dreamland_9200_english.png`
- **M** `game/resources/phase_4/maps/minnies_melody_land_4100_english.png`
- **M** `game/resources/phase_4/maps/minnies_melody_land_4200_english.png`
- **M** `game/resources/phase_4/maps/minnies_melody_land_4300_english.png`
- **M** `game/resources/phase_4/maps/sign_daisysGarden.png`
- **M** `game/resources/phase_4/maps/sign_donaldSdock.png`
- **M** `game/resources/phase_4/maps/sign_minnies_melodyland.png`
- **M** `game/resources/phase_4/maps/the_burrrgh_3100_english.png`
- **M** `game/resources/phase_4/maps/the_burrrgh_3200_english.png`
- **M** `game/resources/phase_4/maps/toontown_central_2100_english.png`
- **M** `game/resources/phase_4/maps/toontown_central_2200_english.png`
- **M** `game/resources/phase_4/maps/toontown_central_2300_english.png`
- **M** `game/resources/phase_5/dna/toontown_central_2100.dna`
- **M** `game/resources/phase_5/dna/toontown_central_2200.dna`
- **M** `game/resources/phase_5/dna/toontown_central_2300.dna`
- **M** `game/resources/phase_6/dna/donalds_dock_1100.dna`
- **M** `game/resources/phase_6/dna/donalds_dock_1200.dna`
- **M** `game/resources/phase_6/dna/donalds_dock_1300.dna`
- **M** `game/resources/phase_6/dna/donalds_dock_sz.dna`
- **M** `game/resources/phase_6/dna/golf_zone_sz.dna`
- **M** `game/resources/phase_6/dna/goofy_speedway_sz.dna`
- **M** `game/resources/phase_6/dna/minnies_melody_land_4100.dna`
- **M** `game/resources/phase_6/dna/minnies_melody_land_4200.dna`
- **M** `game/resources/phase_6/dna/minnies_melody_land_4300.dna`
- **M** `game/resources/phase_6/dna/minnies_melody_land_sz.dna`
- **M** `game/resources/phase_6/dna/outdoor_zone_sz.dna`
- **M** `game/resources/phase_6/dna/storage_GZ_sz.dna`
- **M** `game/resources/phase_6/dna/storage_OZ_sz.dna`
- **M** `game/resources/phase_8/dna/daisys_garden_5100.dna`
- **M** `game/resources/phase_8/dna/daisys_garden_5200.dna`
- **M** `game/resources/phase_8/dna/daisys_garden_5300.dna`
- **M** `game/resources/phase_8/dna/daisys_garden_sz.dna`
- **M** `game/resources/phase_8/dna/donalds_dreamland_9100.dna`
- **M** `game/resources/phase_8/dna/donalds_dreamland_9200.dna`
- **M** `game/resources/phase_8/dna/donalds_dreamland_sz.dna`
- **M** `game/resources/phase_8/dna/the_burrrgh_3100.dna`
- **M** `game/resources/phase_8/dna/the_burrrgh_3200.dna`
- **M** `game/resources/phase_8/dna/the_burrrgh_3300.dna`
- **M** `game/resources/phase_8/dna/the_burrrgh_sz.dna`
- **M** `game/resources/phase_8/maps/GS_signBIG_BR.png`

The two Gag Shop sign texture replacements are:

- **M** `game/resources/phase_3.5/maps/GS_sign.png`
- **M** `game/resources/phase_8/maps/GS_signBIG_BR.png`

### New authored resources

- **A** `game/resources/phase_4/maps/sign_central_commons.png`
- **A** `game/resources/phase_4/maps/sign_moonlight_meadows.png`
- **A** `game/resources/phase_6/models/golf/acorn_NoSign_entrance.bam`
- **A** `game/resources/phase_6/models/golf/acorn_entrance.bam`

## Bundle, launcher source, and documentation

### Bundle entry points and project documentation

- **B** `.gitattributes`
- **B** `.gitignore`
- **B** `1 - Open Town Server GUI.bat`
- **B** `2 - Open Town Client.bat`
- **B** `ARCHITECTURE_LAYOUT.md`
- **B** `Build Windows Launcher.bat`
- **B** `BUILDING.md`
- **B** `CUSTOM_FEATURES.md`
- **B** `LICENSE`
- **B** `Open Town Launcher.bat`
- **B** `Open Town Launcher.command`
- **B** `open-town-launcher.sh`
- **B** `README.md`
- **B** `README_LOCAL.md`
- **B** `Setup OpenToon.bat`
- **B** `Setup OpenToon.ps1`
- **B** `Setup OpenToon.command`
- **B** `setup-opentoon.sh`
- **B** `Test Server Lifecycle.bat`
- **B** `THIRD_PARTY_NOTICES.md`
- **B** `VERIFICATION.md`
- **B** `game/PPYTHON_PATH.example`

### Launcher source and build definitions

- **B** `launcher/build_linux.sh`
- **B** `launcher/build_macos.sh`
- **B** `launcher/build_windows.ps1`
- **B** `launcher/requirements-build.txt`
- **B** `launcher/src/open_toontown_launcher.py`

### Change records intended for `/changes`

- **B** `changes/2026-07-25.md`
- **B** `changes/2026-07-26.md`
- **B** `changes/FILE_INVENTORY.md`
- **B** `changes/FEATURE_AUDIT.md`
- **B** `changes/PROJECT_NAME.md`
- **B** `changes/README.md`
- **B** `changes/STINKY_MAX_PROFILE.md`
- **B** `changes/TODO.md`

## Generated build artifact

- **G** `launcher/dist/windows/OpenTownLauncher.exe`

The executable should be reproducible from the launcher source and build definitions above. Prefer attaching it to a GitHub Release instead of reviewing it as source.

## Local-only and excluded paths

These are deliberately outside the publishable source/resource inventory.

### Runtime logs and transient server state

- Exclude `FULL_FILE_INDEX.txt`; it includes local runtime and database paths.
- Exclude `game/logs/`.
- Exclude `game/astron/logs/`.
- Exclude `game/runtime-control/logs/`, including the current `ai`, `astron`, `client`, and `uberdog` standard-output and standard-error logs.
- Exclude any process-ID, lock, or transient state files created under `game/runtime-control/`.

### Caches and build intermediates

- Exclude every `__pycache__/` directory and every `*.pyc` file.
- Exclude `launcher/.build/`.
- Exclude `launcher/.build-tools/`.
- Exclude platform metadata such as `.DS_Store` and `Thumbs.db`.
- Exclude `runtime/`; it is a bundled third-party runtime, not authored project source.
- Exclude `game/resources/`; its upstream notice does not provide an
  open-source distribution license.
- Exclude `game/astron/win32/`, `game/astron/darwin/`, and
  `game/astron/linux/`; native executables require separate licensing and
  platform review.

### Live Astron database

- Exclude the live database directory `game/astron/databases/astrondb/`.
- Its current local files include `.gitignore`, `100000000.yaml`, `100000001.yaml`, and `info.yaml`; these are runtime/player data, not source.

### Stinky backup

Keep this recovery snapshot local and do not publish it:

- `backups/stinky-max-20260725-134349/astrondb/.gitignore`
- `backups/stinky-max-20260725-134349/astrondb/100000000.yaml`
- `backups/stinky-max-20260725-134349/astrondb/100000001.yaml`
- `backups/stinky-max-20260725-134349/astrondb/info.yaml`

The backup contains the pre-edit Astron database state for Stinky and may contain private player/account data.
