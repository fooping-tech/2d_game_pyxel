from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SceneChange:
    next_scene: str
    payload: dict


class Scene(Protocol):
    name: str

    def enter(self, payload: dict) -> None: ...
    def update(self, dt: float, inp) -> SceneChange | None: ...
    def draw(self) -> None: ...

