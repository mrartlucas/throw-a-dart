from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

PLAYER_COLORS = (
    (58, 137, 255),
    (239, 69, 74),
    (62, 194, 92),
    (255, 211, 58),
)

# Development build lock: progression data exists, but every show and act is
# selectable on the cabinet while mechanics are being tuned.
TEST_MODE = True

# Universal THROW READY timing at the cabinet's 30 FPS target.
# It is a steady fighting-game-style cue: hold for 3 seconds, then disappear.
READY_HOLD_SECONDS = 3
READY_HOLD_FRAMES = 30 * READY_HOLD_SECONDS


@dataclass(frozen=True)
class ActSpec:
    name: str
    menu_name: str
    mechanic_profile: int
    # Reserved for a later score-based progression pass if desired. The current
    # cabinet-test star rule is intentionally based on hits so every act reads
    # consistently while target values are still being tuned.
    star_thresholds: tuple[int, int, int]


@dataclass(frozen=True)
class ShowSpec:
    name: str
    menu_name: str
    acts: tuple[ActSpec, ActSpec, ActSpec]


SHOWS = (
    ShowSpec(
        name="BIG TOP TARGET GALLERY",
        menu_name="BIG TOP",
        acts=(
            ActSpec("BULLSEYES", "BULLSEYES", 0, (100, 250, 450)),
            ActSpec("CRITTER GALLERY", "CRITTERS", 1, (125, 300, 500)),
            ActSpec("BALLOON BURST", "BALLOONS", 2, (150, 325, 525)),
        ),
    ),
    ShowSpec(
        name="MIDWAY MAYHEM",
        menu_name="MIDWAY",
        acts=(
            ActSpec("CLOWN GALLERY", "CLOWNS", 2, (175, 350, 550)),
            ActSpec("PRIZE BOOTH KNOCKDOWN", "PRIZE BOOTH", 0, (200, 375, 575)),
            ActSpec("POOP PLOP PANIC", "POOP PLOP", 2, (225, 400, 600)),
        ),
    ),
    ShowSpec(
        name="SPECIALTY CHALLENGE",
        menu_name="SPECIALTY",
        acts=(
            ActSpec("PINBALL PANIC", "PINBALL", 3, (250, 425, 625)),
            ActSpec("JOKERS WILD", "JOKERS WILD", 3, (275, 450, 650)),
            ActSpec("HORSE PLAY", "HORSE PLAY", 3, (300, 475, 675)),
        ),
    ),
)


class Phase(str, Enum):
    SHOW_SELECT = "show_select"
    ACT_SELECT = "act_select"
    PLAYER_SELECT = "player_select"
    ACT_INTRO = "act_intro"
    PLAYING = "playing"
    GAME_RESULT = "game_result"


@dataclass
class CircusGameState:
    player_count: int = 1
    selected_show: int = 0
    selected_act: int = 0
    current_player: int = 0
    show_index: int = 0
    act_index: int = 0
    throws_per_act: int = 5
    scores: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    combo: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    throws_by_player: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    hits_by_player: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    # Best stars earned per act during this test session.
    stars: list[list[int]] = field(default_factory=lambda: [[0, 0, 0] for _ in range(3)])
    # Stars earned by the run that just ended. This is what RESULT displays.
    result_stars: int = 0
    phase: Phase = Phase.SHOW_SELECT
    phase_frames: int = 0
    last_message: str = ""
    last_points: int = 0
    last_player: int = 0
    message_frames: int = 0
    ready_frames: int = 0

    @property
    def selected_show_spec(self) -> ShowSpec:
        return SHOWS[self.selected_show]

    @property
    def selected_act_spec(self) -> ActSpec:
        return self.selected_show_spec.acts[self.selected_act]

    @property
    def active_act_spec(self) -> ActSpec:
        return SHOWS[self.show_index].acts[self.act_index]

    @property
    def difficulty_rank(self) -> int:
        return self.show_index * 3 + self.act_index

    @property
    def mechanic_profile(self) -> int:
        return self.active_act_spec.mechanic_profile

    def set_players(self, count: int) -> None:
        self.player_count = max(1, min(4, count))

    def is_show_unlocked(self, show_index: int) -> bool:
        if TEST_MODE:
            return True
        if show_index == 0:
            return True
        return all(stars >= 1 for stars in self.stars[show_index - 1])

    def is_act_unlocked(self, show_index: int, act_index: int) -> bool:
        if TEST_MODE:
            return True
        if not self.is_show_unlocked(show_index):
            return False
        if act_index == 0:
            return True
        return self.stars[show_index][act_index - 1] >= 1

    def cycle_show(self, delta: int) -> None:
        for _ in range(len(SHOWS)):
            candidate = (self.selected_show + delta) % len(SHOWS)
            self.selected_show = candidate
            self.selected_act = 0
            if self.is_show_unlocked(candidate):
                return

    def cycle_act(self, delta: int) -> None:
        count = len(self.selected_show_spec.acts)
        for _ in range(count):
            candidate = (self.selected_act + delta) % count
            self.selected_act = candidate
            if self.is_act_unlocked(self.selected_show, candidate):
                return

    def go_shows(self) -> None:
        self.phase = Phase.SHOW_SELECT

    def go_acts(self) -> None:
        self.phase = Phase.ACT_SELECT

    def go_players(self) -> None:
        self.phase = Phase.PLAYER_SELECT

    def begin(self) -> None:
        self.current_player = 0
        self.show_index = self.selected_show
        self.act_index = self.selected_act
        self.scores[:] = [0] * 4
        self.combo[:] = [0] * 4
        self.throws_by_player[:] = [0] * 4
        self.hits_by_player[:] = [0] * 4
        self.result_stars = 0
        self.last_message = ""
        self.last_points = 0
        self.last_player = 0
        self.message_frames = 0
        self.ready_frames = 0
        self.phase = Phase.ACT_INTRO
        self.phase_frames = 42

    def begin_play(self) -> None:
        self.phase = Phase.PLAYING
        self.start_ready_hold()

    def start_ready_hold(self) -> None:
        self.ready_frames = READY_HOLD_FRAMES

    def ready_visible(self) -> bool:
        return self.ready_frames > 0

    def throws_remaining(self) -> int:
        return max(0, self.throws_per_act - self.throws_by_player[self.current_player])

    def _advance_after_throw(self) -> str:
        for step in range(1, self.player_count + 1):
            player = (self.current_player + step) % self.player_count
            if self.throws_by_player[player] < self.throws_per_act:
                self.current_player = player
                return "continue"
        self._record_stars()
        self.phase = Phase.GAME_RESULT
        return "game_over"

    def record_throw(self, base: int) -> tuple[int, str]:
        if self.phase is not Phase.PLAYING:
            return 0, "ignored"
        scoring_player = self.current_player
        self.last_player = scoring_player
        self.throws_by_player[scoring_player] += 1
        if base > 0:
            self.hits_by_player[scoring_player] += 1
            multiplier = 1 + min(self.combo[scoring_player], 2)
            points = base * multiplier
            self.scores[scoring_player] += points
            self.combo[scoring_player] += 1
            self.last_message = "HIT"
            self.last_points = points
        else:
            points = 0
            self.combo[scoring_player] = 0
            self.last_message = "MISS"
            self.last_points = 0
        self.message_frames = 18
        transition = self._advance_after_throw()
        if transition == "continue":
            self.start_ready_hold()
        else:
            self.ready_frames = 0
        return points, transition

    def _record_stars(self) -> None:
        # Cabinet-test rule: stars describe this run's hit consistency, not the
        # point values (which are still being tuned by act).
        best_hits = max(self.hits_by_player[: self.player_count])
        earned = self.stars_for_hits(best_hits, self.throws_per_act)
        self.result_stars = earned
        self.stars[self.show_index][self.act_index] = max(
            self.stars[self.show_index][self.act_index], earned
        )

    @staticmethod
    def stars_for_hits(hits: int, throws: int = 5) -> int:
        if hits <= 0 or throws <= 0:
            return 0
        if hits >= throws:
            return 3
        # For the standard 5-throw act: 3-4 hits = 2 stars.
        if hits * 5 >= throws * 3:
            return 2
        # Any successful hit earns at least one star in the test progression.
        return 1

    def stars_for_selected(self) -> int:
        return self.stars[self.selected_show][self.selected_act]

    def tick_presentation(self) -> None:
        if self.message_frames > 0:
            self.message_frames -= 1
        elif self.ready_frames > 0:
            self.ready_frames -= 1

    def winner(self) -> int:
        return max(range(self.player_count), key=lambda i: self.scores[i])
