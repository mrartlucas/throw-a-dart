from __future__ import annotations

import numpy as np
import pygame


class ArcadeAudio:
    """Small synthesized placeholder UI sound set.

    No external audio assets are required, so this is safe for the mechanics
    build and can be swapped for final authored sounds later.
    """

    SAMPLE_RATE = 22050

    def __init__(self) -> None:
        self.enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=self.SAMPLE_RATE,
                    size=-16,
                    channels=1,
                    buffer=256,
                )
            self._sounds = {
                "move": self._melody(((760, 0.035),)),
                "select": self._melody(((620, 0.035), (920, 0.055))),
                "back": self._melody(((700, 0.035), (430, 0.055))),
                "ready": self._melody(
                    ((660, 0.045), (880, 0.045), (1180, 0.075)),
                    gap=0.008,
                    volume=0.28,
                ),
            }
            self.enabled = True
        except (pygame.error, ValueError):
            self.enabled = False
            self._sounds = {}

    @staticmethod
    def _envelope(length: int) -> np.ndarray:
        if length <= 1:
            return np.ones(max(1, length), dtype=np.float32)
        attack = max(1, min(length // 6, 80))
        release = max(1, min(length // 3, 160))
        env = np.ones(length, dtype=np.float32)
        env[:attack] = np.linspace(0.0, 1.0, attack, endpoint=False, dtype=np.float32)
        env[-release:] = np.linspace(1.0, 0.0, release, endpoint=True, dtype=np.float32)
        return env

    def _tone(self, frequency: float, duration: float, volume: float) -> np.ndarray:
        length = max(1, int(self.SAMPLE_RATE * duration))
        t = np.arange(length, dtype=np.float32) / self.SAMPLE_RATE
        wave = np.sin(2.0 * np.pi * frequency * t)
        wave += 0.22 * np.sin(2.0 * np.pi * frequency * 2.0 * t)
        wave *= self._envelope(length) * volume
        return wave.astype(np.float32)

    def _melody(
        self,
        notes: tuple[tuple[float, float], ...],
        gap: float = 0.0,
        volume: float = 0.20,
    ) -> pygame.mixer.Sound:
        chunks: list[np.ndarray] = []
        gap_samples = max(0, int(self.SAMPLE_RATE * gap))
        silence = np.zeros(gap_samples, dtype=np.float32)
        for index, (frequency, duration) in enumerate(notes):
            chunks.append(self._tone(frequency, duration, volume))
            if gap_samples and index < len(notes) - 1:
                chunks.append(silence)
        wave = np.concatenate(chunks)
        pcm = np.clip(wave * 32767.0, -32768, 32767).astype(np.int16)
        return pygame.sndarray.make_sound(pcm)

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def move(self) -> None:
        self.play("move")

    def select(self) -> None:
        self.play("select")

    def back(self) -> None:
        self.play("back")

    def ready(self) -> None:
        self.play("ready")
