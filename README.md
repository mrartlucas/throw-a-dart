# Throw a Dart v0.2.2

Bullseye Big Top Circus mechanics test build.

## Setup flow

**ACT → PLAYERS → START**

ACT lets us jump directly into one temporary mechanics stage:
- BIG TOP: stationary bullseyes
- MIDWAY: horizontal movers
- BALLOONS: rising targets + pop-up target
- FINALE: mixed target behaviors

Player select follows the Throw A Way Games lower-screen standard:
- `PLAYERS` header
- `1 2 3 4` across the screen
- selected number in yellow
- small yellow arrow directly underneath
- `A START` left / `B BACK` right

## Gameplay changes

- No forced dart-removal turn gate.
- Semantic tracking still prevents a retained dart from repeatedly scoring.
- A dart moved to a new physical coordinate is a new throw.
- 1-4 player turns rotate immediately after a valid throw.
- Five throws per player in the selected test act.
- Simple hit streak multiplier caps at x3.
- Lower screen alternates between current gameplay state and THROW READY while the main 128x128 target field keeps moving.

## Current goal

This is still temporary mechanics art. Test target size, speed, forgiveness, pop-up timing, multiplayer rhythm, and lower-screen readability before final Bullseye Big Top Circus stage design.
