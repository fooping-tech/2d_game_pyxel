from __future__ import annotations

import random
from dataclasses import asdict, dataclass

from game.util import clamp


@dataclass(frozen=True)
class CharacterSpec:
    eye_style: str
    mouth_style: str
    hat_style: str
    speed_mult: float
    jump_mult: float
    charge_mult: float
    base_hp: int
    gravity_mult: float

    def effective(self) -> "CharacterSpec":
        return CharacterSpec(
            eye_style=self.eye_style,
            mouth_style=self.mouth_style,
            hat_style=self.hat_style,
            speed_mult=clamp(float(self.speed_mult), 0.75, 1.25),
            jump_mult=clamp(float(self.jump_mult), 0.75, 1.25),
            charge_mult=clamp(float(self.charge_mult), 0.65, 1.35),
            base_hp=max(1, min(8, int(self.base_hp))),
            gravity_mult=clamp(float(self.gravity_mult), 0.75, 1.25),
        )

    @classmethod
    def from_seed(cls, seed: int) -> "CharacterSpec":
        rng = random.Random(seed)

        # Normalize so the total "power budget" is consistent across characters.
        # We treat gravity as "floatiness" (lower gravity is better), and then
        # invert back to a gravity multiplier for the actual physics.
        total_budget = 5.0  # baseline: 1.0 each for (speed, jump, charge, hp, float)
        min_stat = 0.78
        max_stat = 1.22
        max_tries = 64

        # HP is discrete in gameplay; keep it near 3 but allow variation.
        base_hp = rng.choice([2, 3, 3, 3, 3, 4, 4, 5])
        hp_stat = base_hp / 3.0
        remaining = total_budget - hp_stat

        speed_mult = 1.0
        jump_mult = 1.0
        charge_mult = 1.0
        float_stat = 1.0
        for _ in range(max_tries):
            raw = [rng.uniform(min_stat, max_stat) for _ in range(4)]
            s = sum(raw)
            if s <= 1e-6:
                continue
            k = remaining / s
            cand = [v * k for v in raw]
            if all(min_stat <= v <= max_stat for v in cand):
                speed_mult, jump_mult, charge_mult, float_stat = cand
                break
        gravity_mult = 1.0 / max(0.10, float_stat)

        return cls(
            eye_style=rng.choice(["dot", "sleepy", "angry"]),
            mouth_style=rng.choice(["smile", "flat", "fang"]),
            hat_style=rng.choice(["none", "triangle", "halo"]),
            speed_mult=float(speed_mult),
            jump_mult=float(jump_mult),
            charge_mult=float(charge_mult),
            base_hp=int(base_hp),
            gravity_mult=float(gravity_mult),
        ).effective()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterSpec":
        return cls(
            eye_style=str(data.get("eye_style", "dot")),
            mouth_style=str(data.get("mouth_style", "smile")),
            hat_style=str(data.get("hat_style", "none")),
            speed_mult=float(data.get("speed_mult", 1.0)),
            jump_mult=float(data.get("jump_mult", 1.0)),
            charge_mult=float(data.get("charge_mult", 1.0)),
            base_hp=int(data.get("base_hp", 3)),
            gravity_mult=float(data.get("gravity_mult", 1.0)),
        ).effective()
