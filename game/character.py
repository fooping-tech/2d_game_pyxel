from __future__ import annotations

import random
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CharacterSpec:
    eye_style: str
    mouth_style: str
    hat_style: str

    @classmethod
    def from_seed(cls, seed: int) -> "CharacterSpec":
        rng = random.Random(seed)
        return cls(
            eye_style=rng.choice(["dot", "sleepy", "angry"]),
            mouth_style=rng.choice(["smile", "flat", "fang"]),
            hat_style=rng.choice(["none", "triangle", "halo"]),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterSpec":
        return cls(
            eye_style=str(data.get("eye_style", "dot")),
            mouth_style=str(data.get("mouth_style", "smile")),
            hat_style=str(data.get("hat_style", "none")),
        )

