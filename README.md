# Throw a Dart v0.3.4

Bullseye Big Top Circus mechanics test build.

## Setup flow

**SHOWS -> ACTS -> PLAYERS -> START**

There is no Arcade / Pro selector. Difficulty comes from the ACT progression and its changing challenges.

TEST MODE keeps every show and every act unlocked so cabinet testing can jump directly to any challenge.

## Lower 64x32 screen layout

The lower screen follows one consistent hierarchy:

- top row: small status
- middle row: large focal information
- bottom row: small support / helper information

Gameplay HUD lock:

- **left:** 3 star slots
- **center:** ACT number
- **right:** 5 dart icons
- used darts grey out as throws are spent
- **middle:** large score
- **bottom:** small player / combo support

## THROW READY

`THROW READY` is now a 1.5-second animated cue.

During the cue:

- top 128x128 border rapidly cycles player color / gold / teal / white
- corner accents chase/pulse without covering targets
- lower 64x32 border cycles with the same rhythm
- THROW / READY text alternates color and shifts by one pixel for a tiny arcade bounce
- a short ready chime plays once when the cue becomes visible

After 1.5 seconds, the normal gameplay HUD returns while the player aims.

## Placeholder UI audio

The mechanics build now has synthesized placeholder cabinet sounds with no external audio files required:

- menu move
- select / confirm
- back
- THROW READY chime

These are temporary and can be replaced by the final shared Throw A Way Games sound set later.

## TEST font lab

Because final title / marquee / playfield typography is normally custom artwork, the font lab is only for **coded UI text**.

From the root **SHOWS** screen in TEST MODE:

- **B** = open FONT LAB
- **Left / Right** = cycle font option
- **A** = preview the 1.5-second THROW READY animation/chime on both displays
- **B** = return to SHOWS

The lab compares the same UI examples on the 128x128 top screen and the real 64x32 lower screen so cabinet readability can be judged before we lock the universal UI font.

## Test star rule

Stars are currently based on hit consistency rather than target point values while mechanics are still being tuned:

- 0 hits = 0 stars
- 1-2 hits = 1 star
- 3-4 hits = 2 stars
- 5/5 hits = 3 stars

The RESULT screen shows stars from the current run. The ACT menu may retain the best stars earned during the current test session. Progression data exists, but TEST MODE does not enforce locks.

## Current goal

Keep this mechanics-first. Playtest target size, movement speed, forgiveness, popup timing, act difficulty progression, multiplayer rhythm, HUD readability, UI font readability, sound timing, and physical dart flow before final target-stage art is produced.
