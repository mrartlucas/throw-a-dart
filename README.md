# Throw a Dart v0.3.3

Bullseye Big Top Circus mechanics test build.

## Setup flow

**SHOWS -> ACTS -> PLAYERS -> START**

There is no Arcade / Pro selector. Difficulty comes from the ACT progression and its changing challenges.

TEST MODE keeps every show and every act unlocked so cabinet testing can jump directly to any challenge.

## Lower 64x32 screen layout

The lower screen now follows one consistent hierarchy:

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

SHOWS, ACTS, PLAYERS, and RESULT use the small-header / large-middle / small-helper structure. GET READY remains a large focal cue.

## THROW READY

`THROW READY` appears steadily for 3 seconds when a throw becomes playable, then disappears while the player aims. It returns for the next playable throw. No flashing.

## Test star rule

Stars are currently based on hit consistency rather than target point values while mechanics are still being tuned:

- 0 hits = 0 stars
- 1-2 hits = 1 star
- 3-4 hits = 2 stars
- 5/5 hits = 3 stars

The RESULT screen shows stars from the current run. The ACT menu may retain the best stars earned during the current test session. Progression data exists, but TEST MODE does not enforce locks.

## Current goal

Keep this mechanics-first. Playtest target size, movement speed, forgiveness, popup timing, act difficulty progression, multiplayer rhythm, HUD readability, and physical dart flow before final target-stage art is produced.
