from __future__ import annotations

# Candidate shared Throw A Way Games coded-UI lock, approved on cabinet.
UI_FONT_STYLE = "PIXEL"

# Lower 64x32 screen anchors. Keep these fixed across menu/game/result states.
LOWER_HEADER_Y = 130
LOWER_MAIN_Y = 139
LOWER_HELP_Y = 153
MENU_ARROW_LEFT_X = 2
MENU_ARROW_RIGHT_X = 59
MENU_ARROW_Y = 141

# THROW READY approved treatment.
READY_EFFECT = "COLOR PULSE"
READY_SPEED = "FAST"
READY_SPEED_DIVISOR = 2

# Preferred cabinet speeds captured during Animation Lab testing.
# Index order matches ui_lab.FX_NAMES.
PREFERRED_FX_SPEED_INDEX = (
    1,  # COLOR BORDER = MED
    1,  # CHASE BORDER = MED (not locked, neutral default)
    1,  # TEXT POP = MED
    1,  # BOUNCE = MED
    1,  # FLASH INVERT = MED
    2,  # COLOR PULSE = FAST
    2,  # COMBO = FAST
)
