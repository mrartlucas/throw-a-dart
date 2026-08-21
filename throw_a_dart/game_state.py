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

# Universal THROW READY timing: three short flashes, then stay off until the next throw.
READY_FLASH_ON_FRAMES = 6
READY_FLASH_OFF_FRAMES = 6
READY_FLASH_COUNT = 3
READY_FLASH_TOTAL_FRAMES = (READY_FLASH_ON_FRAMES + READY_FLASH_OFF_FRAMES) * READY_FLASH_COUNT


@dataclass(frozen=True)
class ActSpec:
    name: str
    menu_name: str
    mechanic_profile: int
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
    stars: list[list[int]] = field(default_factory=lambda: [[0, 0, 0] for _ in range(3)])
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
        self.last_message = ""
        self.last_points = 0
        self.last_player = 0
        self.message_frames = 0
        self.ready_frames = 0
        self.phase = Phase.ACT_INTRO
        self.phase_frames = 42

    def begin_play(self) -> None:
        self.phase = Phase.PLAYING
        self.start_ready_flash()

    def start_ready_flash(self) -> None:
        self.ready_frames = READY_FLASH_TOTAL_FRAMES

    def ready_visible(self) -> bool:
        if self.ready_frames <= 0:
            return False
        elapsed = READY_FLASH_TOTAL_FRAMES - self.ready_frames
        cycle = READY_FLASH_ON_FRAMES + READY_FLASH_OFF_FRAMES
        return (elapsed % cycle) < READY_FLASH_ON_FRAMES

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
        self.start_ready_flash()
        return points, self._advance_after_throw()

    def _record_stars(self) -> None:
        # Development-only in-memory progression. Persistence/profile ownership
        # comes later. Test mode never uses this to lock the menu.
        score = max(self.scores[: self.player_count])
        earned = self.stars_for_score(score, self.active_act_spec.star_thresholds)
        self.stars[self.show_index][self.act_index] = max(
            self.stars[self.show_index][self.act_index], earned
        )

    @staticmethod
    def stars_for_score(score: int, thresholds: tuple[int, int, int]) -> int:
        return sum(1 for threshold in thresholds if score >= threshold)

    def stars_for_selected(self) -> int:
        return self.stars[self.selected_show][self.selected_act]

    def tick_presentation(self) -> None:
        if self.message_frames > 0:
            self.message_frames -= 1
        elif self.ready_frames > 0:
            self.ready_frames -= 1

    def winner(self) -> int:
        return max(range(self.player_count), key=lambda i: self.scores[i])
