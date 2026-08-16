# Throw a Dart

Phase-1 Throw A Way Games prototype for the Dartsnut / PixelDarts cabinet.

## Current vertical slice: Bullseye Big Top Circus

This build replaces the original random-circle starter loop with a reusable target engine and a short four-act Circus test show:

1. **BIG TOP** - stationary bullseyes
2. **MIDWAY** - horizontal moving targets
3. **BALLOONS** - rising balloons plus a pop-up clown target
4. **FINALE** - mixed target behaviors

Each player receives 5 throws per act. 1-4 players use the shared Throw A Way Games colors: Blue, Red, Green, Yellow.

## Platform rules already implemented

- 128x160 RGB framebuffer
- main gameplay on 128x128
- lower physical display only uses x=0..63, y=128..159
- lower-right packed region is forced black
- dual-screen loading progress presentation
- semantic dart tracking using active dart coordinates
- retained darts cannot repeatedly score
- game waits for physical removal after each scored/missed throw
- darts present during loading/setup/act transitions are baselined and ignored

## Controls

On player select:

- Left/Down: fewer players (wraps 1 -> 4)
- Right/Up: more players (wraps 4 -> 1)
- A: start

At final results:

- A: play again
- B: return to player select

No artificial aiming reticle is used. The physical dart is the aim.

## Play-test goals

This is intentionally not finished art. Test these on the real board before expanding the Circus:

- target radius / hit forgiveness
- horizontal target speed
- balloon rise speed
- pop-up timing
- number of simultaneous targets
- removal flow between throws
- readability of the 64x32 lower screen
