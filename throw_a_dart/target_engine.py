from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import math, random

PLAY_W = 128
PLAY_H = 128

class TargetBehavior(str, Enum):
    STATIONARY = "stationary"
    HORIZONTAL = "horizontal"
    RISING = "rising"
    POPUP = "popup"

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

    def contains(self, x: int, y: int, forgiveness: int = 3) -> bool:
        if not self.visible or self.hit:
            return False
        r = self.radius + forgiveness
        return (self.x - x) ** 2 + (self.y - y) ** 2 <= r * r

@dataclass(frozen=True)
class HitResult:
    hit: bool
    points: int
    target_id: int | None

class TargetField:
    def __init__(self, seed: int = 20260816) -> None:
        self.rng = random.Random(seed)
        self.targets: list[Target] = []
        self._next_id = 1
        self.frame = 0

    def _add(self, **kw) -> None:
        self.targets.append(Target(target_id=self._next_id, **kw))
        self._next_id += 1

    def reset(self) -> None:
        self.targets.clear(); self.frame = 0

    def start_act(self, act: int) -> None:
        self.reset()
        if act == 0:
            for x, y, r, v in ((27,45,13,25),(64,72,12,50),(101,43,11,100)):
                self._add(behavior=TargetBehavior.STATIONARY,x=x,y=y,radius=r,value=v)
        elif act == 1:
            for y,left in ((34,True),(66,False),(98,True)):
                self._spawn_horizontal(y,left)
        elif act == 2:
            for x in (26,64,102): self._spawn_rising(x)
            self._add(behavior=TargetBehavior.POPUP,x=64,y=42,radius=11,value=100)
        else:
            self._spawn_horizontal(34,True); self._spawn_horizontal(78,False)
            self._spawn_rising(36); self._spawn_rising(93)
            self._add(behavior=TargetBehavior.POPUP,x=64,y=52,radius=10,value=150)

    def _spawn_horizontal(self, y: int, left: bool) -> None:
        r=self.rng.choice((9,10,11)); s=self.rng.uniform(.38,.72)
        self._add(behavior=TargetBehavior.HORIZONTAL,x=-r if left else PLAY_W+r,y=y,radius=r,
                  value=self.rng.choice((25,50,75)),vx=s if left else -s,lifetime=520,phase=self.rng.random()*6.28)

    def _spawn_rising(self, x: int) -> None:
        r=self.rng.choice((9,10,11))
        self._add(behavior=TargetBehavior.RISING,x=x,y=PLAY_H+r,radius=r,
                  value=self.rng.choice((25,50,75)),vy=-self.rng.uniform(.24,.42),lifetime=700,phase=self.rng.random()*6.28)

    def update(self, act: int) -> None:
        self.frame += 1
        for t in self.targets: t.update()
        self.targets = [t for t in self.targets if not t.expired]
        if act == 1 and self.frame % 95 == 0 and len(self.targets) < 5:
            self._spawn_horizontal(self.rng.choice((34,57,81,105)), self.rng.choice((True,False)))
        elif act == 2 and self.frame % 115 == 0 and len(self.targets) < 6:
            self._spawn_rising(self.rng.choice((24,46,68,90,108)))
        elif act >= 3:
            if self.frame % 105 == 0 and len(self.targets) < 7:
                self._spawn_horizontal(self.rng.choice((30,54,78,103)), self.rng.choice((True,False)))
            if self.frame % 145 == 0 and len(self.targets) < 7:
                self._spawn_rising(self.rng.choice((22,42,64,86,106)))

    def hit_test(self, x: int, y: int, forgiveness: int = 3) -> HitResult:
        c=[t for t in self.targets if t.contains(x,y,forgiveness)]
        if not c: return HitResult(False,0,None)
        t=min(c,key=lambda z:z.radius); t.hit=True
        return HitResult(True,t.value,t.target_id)
