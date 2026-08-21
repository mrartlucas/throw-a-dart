# Throw a Dart v0.3.5

Bullseye Big Top Circus mechanics test build.

## Setup flow

**SHOWS -> ACTS -> PLAYERS -> START**

There is no Arcade / Pro selector. Difficulty comes from ACT progression and its changing challenges.

TEST MODE keeps every show and act unlocked so cabinet testing can jump directly to any challenge.

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

## TEST LAB

From the root **SHOWS** screen in TEST MODE:

- **B** = open TEST LAB
- **Left / Right** = choose FONT LAB or ANIMATION LAB
- **A** = enter selected lab
- **B** = return

### FONT LAB

The font lab compares coded UI typography only. Final titles, marquees and playfield typography remain custom artwork.

- **Left / Right** = cycle font option
- **A** = preview THROW READY
- **B** = return to TEST LAB

The sample is shown on both the 128x128 main screen and actual 64x32 lower screen.

### ANIMATION LAB

Seven THROW READY treatments are available:

1. COLOR BORDER
2. CHASE BORDER
3. TEXT POP
4. BOUNCE
5. FLASH INVERT
6. COLOR PULSE
7. COMBO

Controls:

- **Left / Right** = previous / next animation
- **Up / Down** = change speed: SLOW / MED / FAST
- **A** = run the 1.5-second preview with ready sound
- **B** = return to TEST LAB

Every preview renders on both physical display regions so the effect can be judged at real cabinet resolution before anything is made universal.

## THROW READY

The live game still uses the current animated THROW READY treatment for 1.5 seconds. The Animation Lab is exploratory only until a treatment and speed are approved.

## Placeholder UI audio

The mechanics build includes synthesized placeholder sounds with no external audio assets required:

- menu move
- select / confirm
- back
- THROW READY chime

These can later become the shared temporary Throw A Way Games sound language.

## Test star rule

Stars are currently based on hit consistency while target point values are still being tuned:

- 0 hits = 0 stars
- 1-2 hits = 1 star
- 3-4 hits = 2 stars
- 5/5 hits = 3 stars

The RESULT screen shows stars from the current run. The ACT menu can retain the best stars earned during the current test session. TEST MODE does not enforce progression locks.

## Current goal

Keep this mechanics-first. Use TEST LAB to lock UI font readability, THROW READY animation style, animation speed and sound feel on the real cabinet. After approval, extract those chosen behaviors into a reusable Throw A Way Games UI/FX layer for Throw a Dart, Throw a Strike and Throw a Ball.
