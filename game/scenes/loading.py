from __future__ import annotations

import pyxel

from game.generation import GenerationJob
from game.scenes.base import SceneChange
from game.theme import build_theme
from game.unicode_text import UnicodeText


class LoadingScene:
    name = "loading"

    def __init__(self, utext: UnicodeText) -> None:
        self._utext = utext
        self._job: GenerationJob | None = None
        self._prompt = ""
        self._bg = 0

    def enter(self, payload: dict) -> None:
        self._prompt = str(payload.get("prompt", ""))
        theme = build_theme(self._prompt or "default")
        self._bg = theme.bg
        # Keep selection BGM during loading.
        self._job = GenerationJob(prompt=self._prompt, seed=theme.seed)
        self._job.start()

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]  # noqa: ARG002
        job = self._job
        if job is None:
            return None
        prog, done, res = job.snapshot()
        if done and res is not None:
            return SceneChange("intro", {"prompt": self._prompt, "character": res.spec.to_dict()})
        return None

    def draw(self) -> None:
        pyxel.cls(self._bg)

        # Title
        title = "生成中..."
        spr = self._utext.render(title, 7)
        self._utext.blit(pyxel.width // 2 - spr.w // 2, 160, title, 7)

        prompt = (self._prompt or "")[:56]
        if prompt:
            spr2 = self._utext.render(prompt, 6)
            self._utext.blit(pyxel.width // 2 - spr2.w // 2, 210, prompt, 6)

        prog = 0.0
        if self._job is not None:
            prog, _, _ = self._job.snapshot()

        bar_w = 520
        bar_h = 18
        x = pyxel.width // 2 - bar_w // 2
        y = 280
        pyxel.rect(x - 2, y - 2, bar_w + 4, bar_h + 4, 0)
        pyxel.rect(x, y, bar_w, bar_h, 5)
        pyxel.rect(x, y, int(bar_w * prog), bar_h, 10)
        pyxel.text(pyxel.width // 2 - 10, y + 30, f"{int(prog*100):3d}%", 7)
