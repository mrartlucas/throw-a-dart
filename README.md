# Throw a Dart v0.3.2

Bullseye Big Top Circus mechanics test build. Gameplay mechanics remain unchanged from the cabinet-approved v0.3.1 pass.

## Cabinet presentation corrections

- Setup remains **SHOWS -> ACTS -> PLAYERS -> START**.
- SHOW selection is larger on the 64x32 screen.
- Result typography is larger on both screens.
- Main 128x128 gameplay no longer duplicates the P1 badge; player identity lives on the lower screen.
- PLAYERS header, numbers, and selector arrow are moved up one pixel.
- Menu and helper text use normal 4 px character spacing whenever it fits. No length-based text crushing.
- Gameplay HUD replaces cryptic `D1 / X3 / A1` shorthand with clear labels: `LEFT`, `SCORE`, `COMBO`, and `ACT`.

## Universal THROW READY behavior

`THROW READY` is a fighting-game-style cue. It now appears steadily for **3 seconds**, then disappears and stays off while the player aims. It returns for 3 seconds when the next throw becomes playable. **No flashing.**

This rule is also locked in the Throw A Way Games UI / Visual Standard.

## Test star rule

Scoring math is unchanged. Stars are now deliberately independent of target point values while mechanics are still being tuned:

- 0 hits = 0 stars
- 1-2 hits = 1 star
- 3-4 hits = 2 stars
- 5/5 hits = 3 stars

The RESULT screen always shows stars from the **current run**. The ACT menu may retain the best stars earned during the test session. This prevents an old 3-star run from appearing after a later all-miss run. TEST MODE still keeps every show and act unlocked.
