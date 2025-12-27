from __future__ import annotations

import random
import os

import pyxel

from game.audio import AudioManager
from game.config import GameConfig
from game.constants import FPS, HEIGHT, WIDTH
from game.dotenv import load_dotenv
from game.input import InputState, read_input
from game.scenes.base import SceneChange
from game.scenes.game_over import GameOverScene
from game.scenes.guardian import GuardianScene
from game.scenes.intro import IntroScene
from game.scenes.loading import LoadingScene
from game.scenes.play import PlayScene
from game.scenes.title import TitleScene
from game.storage import ScoreStore
from game.unicode_text import UnicodeText


class GameApp:
    def __init__(self) -> None:
        load_dotenv()
        pyxel.init(WIDTH, HEIGHT, title="Vertical Jump", fps=FPS)
        self._dt = 1.0 / FPS

        self._cfg = GameConfig.load()
        if self._cfg.lang and str(self._cfg.lang).strip().lower() not in {"", "auto"}:
            os.environ.setdefault("GAME_LANG", str(self._cfg.lang).strip())
        self._audio = AudioManager.create(self._cfg)
        self._scores = ScoreStore()
        self._scores.load()
        self._utext = UnicodeText(font_px=self._cfg.ui_font_px)

        self._scenes = {
            "title": TitleScene(self._audio, self._utext, self._cfg),
            "guardian": GuardianScene(self._audio, self._utext),
            "loading": LoadingScene(self._utext),
            "intro": IntroScene(self._audio, self._utext, self._cfg),
            "play": PlayScene(self._audio, self._utext, self._cfg, rng=random.Random(1234)),
            "game_over": GameOverScene(self._audio, self._scores, self._utext, self._cfg),
        }
        self._current = self._scenes["title"]
        self._current.enter({})

        self._prev_inp: InputState | None = None
        self._audio_unlocked_once = False

    def update(self) -> None:
        inp = read_input(self._prev_inp)
        self._prev_inp = inp
        if (not self._audio_unlocked_once) and (
            inp.left or inp.right or inp.jump_down or inp.confirm or inp.back
        ):
            self._audio.unlock()
            self._audio_unlocked_once = True

        try:
            change = self._current.update(self._dt, inp)
        except SystemExit:
            pyxel.quit()
            return

        if isinstance(change, SceneChange):
            self._current = self._scenes[change.next_scene]
            self._current.enter(change.payload)

    def draw(self) -> None:
        self._current.draw()


def run() -> None:
    app = GameApp()
    pyxel.run(app.update, app.draw)
