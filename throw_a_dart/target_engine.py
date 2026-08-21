from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import math
import random

PLAY_W = 128
PLAY_H = 128

class TargetBehavior(str, Enum):
    STATIONARY = "stationary"
    HORIZONTAL = "horizontal"
    RISING = "rising"
    POPUP = "popup"

@dataclass(frozen=True)
class ActTuning:
    forgiveness: int
    stationary_count: int = 0
    horizontal_count: int = 0
    rising_count: int = 0
    popup_count: int = 0

ACT_TUNING = (
    ActTuning(forgiveness=4, stationary_count=3),
    ActTuning(forgiveness=4, horizontal_count=3),
    ActTuning(forgiveness=4, rising_count=3, popup_count=1),
    ActTuning(forgiveness=3, horizontal_count=2, rising_count=2, popup_count=1),
)

@dataclass
class Target:
    target_id: int
    behavior: TargetBehavior
    x: float
    y: float
    radius: int
    value: int
    vx: float = 0.0
    vy: float = 0.0
    age: int = 0
    lifetime: int = 99999
    visible: bool = True
    hit: bool = False
    phase: float = 0.0

    def update(self) -> None:
        self.age += 1
        if self.hit:
            return
        if self.behavior is TargetBehavior.HORIZONTAL:
            self.x += self.vx
        elif self.behavior is TargetBehavior.RISING:
            self.y += self.vy
            self.x += math.sin(self.age * 0.06 + self.phase) * 0.18
        elif self.behavior is TargetBehavior.POPUP:
            self.visible = 10 <= (self.age % 86) <= 56

    @property
    def expired(self) -> bool:
        if self.hit or self.age >= self.lifetime:
            return True
        if self.behavior is TargetBehavior.HORIZONTAL:
            return self.x < -18 or self.x > PLAY_W + 18
        if self.behavior is TargetBehavior.RISING:
            return self.y < -18
        return False

    def contains(self, x: int, y: int, forgiveness: int) -> bool:
        if not self.visible or self.hit:
            return False
        r = self.radius + forgiveness
        return (self.x - x) ** 2 + (self.y - y) ** 2 <= r * r

@dataclass
class ImpactMarker:
    x: int
    y: int
    hit: bool
    age: int = 0
    lifetime: int = 12

    def update(self) -> None:
        self.age += 1

    @property
    def expired(self) -> bool:
        return self.age >= self.lifetime

@dataclass(frozen=True)
class HitResult:
    hit: bool
    points: int
    target_id: int | None

class TargetField:
    def __init__(self, seed: int = 20260816) -> None:
        self.rng = random.Random(seed)
        self.targets: list[Target] = []
        self.impacts: list[ImpactMarker] = []
        self._next_id = 1
        self.frame = 0
        self.act = 0

    @property
    def tuning(self) -> ActTuning:
        return ACT_TUNING[self.act]

    def _add(self, **kwargs) -> None:
        self.targets.append(Target(target_id=self._next_id, **kwargs))
        self._next_id += 1

    def reset(self) -> None:
        self.targets.clear()
        self.impacts.clear()
        self.frame = 0

    def start_act(self, act: int) -> None:
        self.reset()
        self.act = max(0, min(len(ACT_TUNING) - 1, act))
        if self.act == 0:
            for x, y, r, value in ((27, 45, 13, 25), (64, 72, 12, 50), (101, 43, 11, 100)):
                self._add(behavior=TargetBehavior.STATIONARY, x=x, y=y, radius=r, value=value)
        elif self.act == 1:
            for y, left in ((35, True), (67, False), (99, True)):
                self._spawn_horizontal(y, left)
        elif self.act == 2:
            for x, y in ((26, 104), (64, 78), (102, 52)):
                self._spawn_rising(x, y)
            self._spawn_popup()
        else:
            self._spawn_horizontal(36, True)
            self._spawn_horizontal(86, False)
            self._spawn_rising(38, 103)
            self._spawn_rising(92, 68)
            self._spawn_popup(y=52, radius=10, value=150)

    def _clear_position(self, x: float, y: float, radius: int, padding: int = 7) -> bool:
        for target in self.targets:
            if target.hit:
                continue
            minimum = radius + target.radius + padding
            if (target.x - x) ** 2 + (target.y - y) ** 2 < minimum * minimum:
                return False
        return True

    def _spawn_stationary(self) -> None:
        for _ in range(30):
            radius = self.rng.choice((10, 11, 12, 13))
            x = self.rng.randint(radius + 8, PLAY_W - radius - 8)
            y = self.rng.randint(32 + radius, 104 - radius)
            if self._clear_position(x, y, radius):
                self._add(behavior=TargetBehavior.STATIONARY, x=x, y=y, radius=radius, value=self.rng.choice((25, 50, 75, 100)))
                return

    def _spawn_horizontal(self, y: int | None = None, left: bool | None = None) -> None:
        radius = self.rng.choice((9, 10, 11))
        speed = self.rng.uniform(0.38, 0.72)
        left = self.rng.choice((True, False)) if left is None else left
        y = self.rng.choice((34, 57, 80, 103)) if y is None else y
        self._add(behavior=TargetBehavior.HORIZONTAL, x=-radius if left else PLAY_W + radius, y=y, radius=radius, value=self.rng.choice((25, 50, 75)), vx=speed if left else -speed, lifetime=520, phase=self.rng.random() * 6.28)

    def _spawn_rising(self, x: int | None = None, y: int | None = None) -> None:
        radius = self.rng.choice((9, 10, 11))
        x = self.rng.choice((22, 43, 64, 85, 106)) if x is None else x
        start_y = PLAY_H + radius if y is None else y
        self._add(behavior=TargetBehavior.RISING, x=x, y=start_y, radius=radius, value=self.rng.choice((25, 50, 75)), vy=-self.rng.uniform(0.24, 0.42), lifetime=700, phase=self.rng.random() * 6.28)

    def _spawn_popup(self, x: int = 64, y: int = 43, radius: int = 11, value: int = 100) -> None:
        self._add(behavior=TargetBehavior.POPUP, x=x, y=y, radius=radius, value=value, phase=self.rng.random() * 6.28)

    def _count(self, behavior: TargetBehavior) -> int:
        return sum(1 for target in self.targets if target.behavior is behavior and not target.hit)

    def _replenish(self) -> None:
        tuning = self.tuning
        while self._count(TargetBehavior.STATIONARY) < tuning.stationary_count:
            before = len(self.targets)
            self._spawn_stationary()
            if len(self.targets) == before:
                break
        while self._count(TargetBehavior.HORIZONTAL) < tuning.horizontal_count:
            self._spawn_horizontal()
        while self._count(TargetBehavior.RISING) < tuning.rising_count:
            self._spawn_rising()
        while self._count(TargetBehavior.POPUP) < tuning.popup_count:
            if self.act >= 3:
                self._spawn_popup(y=52, radius=10, value=150)
            else:
                self._spawn_popup()

    def update(self, act: int | None = None) -> None:
        if act is not None:
            self.act = max(0, min(len(ACT_TUNING) - 1, act))
        self.frame += 1
        for target in self.targets:
            target.update()
        for impact in self.impacts:
            impact.update()
        self.targets = [target for target in self.targets if not target.expired]
        self.impacts = [impact for impact in self.impacts if not impact.expired]
        self._replenish()

    def hit_test(self, x: int, y: int, forgiveness: int | None = None) -> HitResult:
        margin = self.tuning.forgiveness if forgiveness is None else forgiveness
        candidates = [target for target in self.targets if target.contains(x, y, margin)]
        if not candidates:
            self.impacts.append(ImpactMarker(x=x, y=y, hit=False))
            return HitResult(False, 0, None)
        target = min(candidates, key=lambda item: item.radius)
        target.hit = True
        self.impacts.append(ImpactMarker(x=int(target.x), y=int(target.y), hit=True))
        return HitResult(True, target.value, target.target_id)
