from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DartSample:
    dart_index: int
    x: int
    y: int

class SemanticDartTracker:
    """One physical placement emits at most one semantic throw."""
    def __init__(self) -> None:
        self._baseline: dict[int, tuple[int, int]] | None = None

    def baseline(self, active: tuple[DartSample, ...]) -> None:
        self._baseline = {d.dart_index: (d.x, d.y) for d in active}

    def observe(self, raw_hits: tuple[DartSample, ...], active: tuple[DartSample, ...]) -> tuple[DartSample, ...]:
        current = {d.dart_index: (d.x, d.y) for d in active}
        if self._baseline is None:
            self._baseline = current
            return ()
        semantic = {d.dart_index: d for d in raw_hits}
        for d in active:
            if self._baseline.get(d.dart_index) != (d.x, d.y):
                semantic.setdefault(d.dart_index, d)
        self._baseline = current
        for d in raw_hits:
            if d.dart_index not in current:
                self._baseline[d.dart_index] = (d.x, d.y)
        return tuple(semantic[i] for i in sorted(semantic))
