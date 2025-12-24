from __future__ import annotations

import pyxel

from game.audio import AudioManager
from game.constants import HEIGHT, WIDTH
from game.scenes.base import SceneChange
from game.storage import RunRecord, ScoreStore
from game.unicode_text import UnicodeText


class GameOverScene:
    name = "game_over"

    def __init__(self, audio: AudioManager, scores: ScoreStore, utext: UnicodeText) -> None:
        self._audio = audio
        self._scores = scores
        self._utext = utext
        self._payload: dict = {}
        self._ranking: list[RunRecord] = []

    def enter(self, payload: dict) -> None:
        self._payload = payload
        self._audio.play("game_over")
        floor = int(payload.get("floor", 0))
        reason = str(payload.get("reason", "defeated"))
        prompt = str(payload.get("prompt", ""))
        try:
            self._scores.record(RunRecord.create(floor=floor, reason=reason, prompt=prompt))
        except Exception:
            pass
        self._ranking = self._scores.top(10)

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]  # noqa: ARG002
        if inp.confirm:
            self._audio.play("ui_confirm")
            return SceneChange("guardian", {})
        if inp.back:
            self._audio.play("ui_confirm")
            return SceneChange("title", {})
        return None

    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.text(WIDTH // 2 - 24, 140, "GAME OVER", 8)

        floor = int(self._payload.get("floor", 0))
        reason = str(self._payload.get("reason", "defeated"))
        pyxel.text(WIDTH // 2 - 36, 220, f"FLOOR: {floor}", 7)
        pyxel.text(WIDTH // 2 - 52, 250, f"HIGHSCORE: {self._scores.highscore}", 6)
        pyxel.text(WIDTH // 2 - 60, 278, f"REASON: {reason}", 5)

        pyxel.text(WIDTH // 2 - 44, 320, "RANKING (TOP 10)", 7)
        y = 348
        for i, r in enumerate(self._ranking[:10], start=1):
            p = (r.prompt or "")[:18]
            self._utext.blit(WIDTH // 2 - 240, y, f"{i:2d}. {r.floor:4d}F  {p}", 6)
            y += 22
            if y > HEIGHT - 160:
                break

        pyxel.text(WIDTH // 2 - 64, HEIGHT - 120, "Enter: retry   Esc: title", 6)
