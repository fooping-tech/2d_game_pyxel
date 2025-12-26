from __future__ import annotations

import pyxel

from game.config import GameConfig
from game.constants import HEIGHT, WIDTH
from game.audio import AudioManager
from game.scenes.base import SceneChange
from game.unicode_text import UnicodeText


class TitleScene:
    name = "title"

    def __init__(self, audio: AudioManager, utext: UnicodeText, cfg: GameConfig) -> None:
        self._audio = audio
        self._utext = utext
        self._cfg = cfg
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
        title = "VERTICAL JUMP"
        spr = self._utext.render(title, 7, self._cfg.title_font_px_big)
        self._utext.blit(WIDTH // 2 - spr.w // 2, 120, title, 7, size_px=self._cfg.title_font_px_big)

        hint1 = "Enter: start   Esc: quit"
        spr1 = self._utext.render(hint1, 6)
        self._utext.blit(WIDTH // 2 - spr1.w // 2, 210, hint1, 6)

        hint2 = "←/→ move  Space/Z charge jump"
        spr2 = self._utext.render(hint2, 6)
        self._utext.blit(WIDTH // 2 - spr2.w // 2, 250, hint2, 6)

        if int(self._t * 2) % 2 == 0:
            press = "PRESS ENTER"
            sprp = self._utext.render(press, 10)
            self._utext.blit(WIDTH // 2 - sprp.w // 2, HEIGHT - 120, press, 10)
