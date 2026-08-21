# Throw a Dart v0.3.0

Bullseye Big Top Circus mechanics/progression test build.

## Setup flow

**SHOWS → ACTS → PLAYERS → START**

There is **no Arcade / Pro selector** in this title. Difficulty comes from the act progression itself: later acts introduce harder target behavior, less forgiveness, faster motion, shorter timing windows, and more complex challenges.

## Show / Act structure

The current development scaffold is 3 shows × 3 acts. Every act maps to one of the reusable target-engine mechanic profiles while we prove cabinet feel before final stage art.

## Player select

Player select follows the Throw A Way Games lower-screen standard:
- `PLAYERS` header
- `1 2 3 4` visible together
- selected number highlighted
- small arrow directly underneath
- `A START` / `B BACK`

## Stars and progression

A 0–3 star result is now calculated for each act.

Planned release behavior:
- 1 star can unlock the next normal act.
- extra stars can support mastery / bonus unlocks.
- achievements can later unlock secret content.

**TEST MODE is ON in v0.3.0.**

That means:
- all shows are selectable
- all acts are selectable
- stars are tracked in memory for tuning
- stars do not lock anything
- no achievement gate blocks cabinet testing

## Difficulty scaffold

The nine act positions have a difficulty rank from 0–8. The target engine now uses that rank to progressively tune:
- hit forgiveness
- target size at higher tiers
- horizontal movement speed
- rising movement speed
- pop-up visibility time

The existing four target-engine profiles remain reusable mechanics scaffolding. Final stage-specific target designs come only after the physical board values are approved.

## Current goal

Playtest the complete setup flow and nine difficulty positions before stage art:
- SHOWS navigation
- ACTS navigation
- PLAYERS row / selector arrow
- target size
- movement speed
- hit forgiveness
- pop-up timing
- multiplayer rhythm
- star thresholds
- lower-screen readability

Final target-stage art remains intentionally parked until these mechanics are locked.
