# Throw a Dart v0.3.1

Bullseye Big Top Circus mechanics test build.

## Setup flow

**SHOWS -> ACTS -> PLAYERS -> START**

- No Arcade / Pro selector. The acts themselves increase difficulty and introduce different challenges.
- Three SHOWS with three ACTS each are wired into the test menu.
- TEST MODE keeps every SHOW and ACT unlocked.
- PLAYERS uses the Throw A Way Games `1 2 3 4` row.
- Player numbers sit one pixel higher and the selected-player marker is a small **upward-pointing** arrow.
- SHOW/ACT navigation uses the series-standard 3x5 edge chevrons.
- Lower-screen helper text keeps the standard 4 px character advance whenever it fits; 3 px is reserved only for genuine overflow.

## Universal THROW READY behavior

`THROW READY` is a fighting-game-style start cue, not a repeating status panel.

- It flashes **3 times** at the start of a playable throw.
- After the third flash it disappears.
- It stays off while the player aims.
- After a valid throw/result, the 3-flash cue is armed again for the next throw.
- It does not alternate forever with the gameplay HUD.

This behavior is also locked in the Throw A Way Games UI / Visual Standard.

## Progression scaffold

- Every act can earn 0-3 stars from score thresholds.
- Stars are tracked in memory for testing.
- They do not lock anything in TEST MODE.
- Final release progression can later use stars to unlock the next act/show while keeping achievements for bonus/secret content.

## Mechanics-first goal

The current playfields are temporary mechanics graphics. Use this build to test target size, target speed, forgiveness, pop-up timing, multiplayer rhythm, difficulty progression, menu readability, and lower-screen behavior before final target-stage artwork is designed.
