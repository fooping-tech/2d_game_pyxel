from __future__ import annotations

import pyxel

from game.audio import AudioManager
from game.backgrounds import zone_for_floor
from game.config import GameConfig
from game.constants import HEIGHT, WIDTH
from game.scenes.base import SceneChange
from game.storage import RunRecord, ScoreStore
from game.unicode_text import UnicodeText


class GameOverScene:
    name = "game_over"

    def __init__(self, audio: AudioManager, scores: ScoreStore, utext: UnicodeText, cfg: GameConfig) -> None:
        self._audio = audio
        self._scores = scores
        self._utext = utext
        self._cfg = cfg
        self._payload: dict = {}
        self._ranking: list[RunRecord] = []

    def enter(self, payload: dict) -> None:
        self._payload = payload
        self._audio.play_bgm("game_over")
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
        title = "GAME OVER"
        spr = self._utext.render(title, 8, self._cfg.game_over_font_px_big)
        self._utext.blit(WIDTH // 2 - spr.w // 2, 140, title, 8, size_px=self._cfg.game_over_font_px_big)

        floor = int(self._payload.get("floor", 0))
        reason = str(self._payload.get("reason", "defeated"))
        zone = zone_for_floor(floor, step=self._cfg.zone_floor_step)
        line1 = f"FLOOR: {floor}"
        line1b = f"STAGE: {zone.name_jp}"
        line2 = f"HIGHSCORE: {self._scores.highscore}"
        line3 = f"REASON: {reason}"
        s1 = self._utext.render(line1, 7)
        s1b = self._utext.render(line1b, 7)
        s2 = self._utext.render(line2, 6)
        s3 = self._utext.render(line3, 5)
        self._utext.blit(WIDTH // 2 - s1.w // 2, 220, line1, 7)
        self._utext.blit(WIDTH // 2 - s1b.w // 2, 246, line1b, 7)
        self._utext.blit(WIDTH // 2 - s2.w // 2, 276, line2, 6)
        self._utext.blit(WIDTH // 2 - s3.w // 2, 304, line3, 5)

        header = "RANKING (TOP 10)"
        sh = self._utext.render(header, 7)
        self._utext.blit(WIDTH // 2 - sh.w // 2, 336, header, 7)
        y = 364
        for i, r in enumerate(self._ranking[:10], start=1):
            p = (r.prompt or "")[:18]
            self._utext.blit(WIDTH // 2 - 240, y, f"{i:2d}. {r.floor:4d}F  {p}", 6)
            y += 22
            if y > HEIGHT - 160:
                break

        hint = "Enter: retry   Esc: title"
        sh2 = self._utext.render(hint, 6)
        self._utext.blit(WIDTH // 2 - sh2.w // 2, HEIGHT - 120, hint, 6)
