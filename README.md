# Throw a Dart v0.2.1

Throw A Way Games target-engine playtest using **Bullseye Big Top Circus** as the vertical slice.

## Mechanics-menu update

Setup now uses the test flow:

**ACT → PLAYERS → START**

- ACT lets us jump directly into one temporary mechanics act.
- PLAYERS shows **1 2 3 4** in one row with a small arrow directly under the selected number.
- B from PLAYERS returns to ACT selection.
- The clearer font treatment from v0.2.0 is retained.

This remains a mechanics build. The real circus target-stage designs come after target size, movement, hit forgiveness, and cabinet flow are locked.

## Included
- 1-4 players: Blue / Red / Green / Yellow
- 128x128 main playfield + real 64x32 lower display region
- lower-right packed framebuffer forced black
- dual-screen loading progress
- semantic dart tracking: one physical placement scores once
- waits for dart removal before the next throw
- 5 throws per player in the selected test act
- combo scoring up to x3

## Four selectable mechanics acts
1. BIG TOP - stationary bullseyes
2. MIDWAY - horizontal movers
3. BALLOONS - rising balloons + pop-up target
4. FINALE - mixed target behaviors

The current art and act names are temporary test scaffolding. The goal is to prove the play mechanics first, then design the actual Bullseye Big Top Circus stages.
