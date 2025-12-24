from __future__ import annotations

import pyxel

from game.constants import HEIGHT, WIDTH
from game.audio import AudioManager
from game.scenes.base import SceneChange


class TitleScene:
    name = "title"

    def __init__(self, audio: AudioManager) -> None:
        self._audio = audio
        self._t = 0.0

    def enter(self, payload: dict) -> None:  # noqa: ARG002
        self._t = 0.0

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]
        self._t += dt
        if inp.confirm:
            self._audio.play("ui_confirm")
            return SceneChange("guardian", {})
        if inp.back:
            raise SystemExit
        return None

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(WIDTH // 2 - 48, 130, "VERTICAL JUMP", 7)
        pyxel.text(WIDTH // 2 - 74, 210, "Enter: start   Esc: quit", 6)
        pyxel.text(WIDTH // 2 - 92, 250, "<-/-> move  Space/Z charge jump", 6)

        if int(self._t * 2) % 2 == 0:
            pyxel.text(WIDTH // 2 - 40, HEIGHT - 110, "PRESS ENTER", 10)
