from __future__ import annotations

from dataclasses import dataclass

import math
import pyxel

from game.audio import AudioManager
from game.constants import HEIGHT, WIDTH
from game.pixel_art import boss_sprite
from game.scenes.base import SceneChange
from game.unicode_text import UnicodeText


@dataclass
class Question:
    prompt: str
    options: list[str]


class GuardianScene:
    name = "guardian"

    def __init__(self, audio: AudioManager, utext: UnicodeText) -> None:
        self._audio = audio
        self._utext = utext
        self._questions: list[Question] = [
            Question("世界観はどれが良い？", ["古代遺跡", "蒸気機関", "深海都市"]),
            Question("色合いはどれだ？", ["寒色", "暖色", "毒々しいネオン"]),
            Question("敵の雰囲気は？", ["ゆるい魔物", "機械兵", "影の獣"]),
            Question("アイテムの質感は？", ["宝石", "薬瓶", "古文書"]),
            Question("塔の危険は何だ？", ["棘", "呪い", "猛風"]),
        ]
        self._guardian_lines = [
            "よく来たなぁ小僧。",
            "私はこの塔の番人だ！ぐはは！",
            "貴様の旅路の“雰囲気”を決めてやろう…。",
            "3択に答えるか、自由に書け！",
        ]

        self._q_index = 0
        self._selection = 0  # 0..2 or 3=free
        self._free_text = ""
        self._answers: list[str] = []

    def enter(self, payload: dict) -> None:  # noqa: ARG002
        self._q_index = 0
        self._selection = 0
        self._free_text = ""
        self._answers = []
        self._audio.play_bgm("select")

    def _append_text(self) -> None:
        if self._selection != 3:
            return

        if pyxel.btnp(pyxel.KEY_BACKSPACE) and self._free_text:
            self._free_text = self._free_text[:-1]
            return

        if len(self._free_text) >= 26:
            return

        # Minimal ASCII input (pyxel doesn't provide IME/unicode input)
        for key, ch in [
            (pyxel.KEY_SPACE, " "),
            (pyxel.KEY_MINUS, "-"),
            (pyxel.KEY_SLASH, "/"),
            (pyxel.KEY_PERIOD, "."),
        ]:
            if pyxel.btnp(key):
                self._free_text += ch
                return

        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                self._free_text += str(i)
                return

        for i in range(26):
            if pyxel.btnp(pyxel.KEY_A + i):
                ch = chr(ord("a") + i)
                if pyxel.btn(pyxel.KEY_SHIFT) or pyxel.btn(pyxel.KEY_LSHIFT) or pyxel.btn(pyxel.KEY_RSHIFT):
                    ch = ch.upper()
                self._free_text += ch
                return

    def _commit_answer(self) -> bool:
        q = self._questions[self._q_index]
        if self._selection == 3:
            text = self._free_text.strip()
            if not text:
                return False
            self._answers.append(text)
        else:
            self._answers.append(q.options[self._selection])
        self._free_text = ""
        self._selection = 0
        self._q_index += 1
        return True

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]  # noqa: ARG002
        if inp.back:
            return SceneChange("title", {})

        if pyxel.btnp(pyxel.KEY_UP):
            self._selection = (self._selection - 1) % 4
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self._selection = (self._selection + 1) % 4
        elif pyxel.btnp(pyxel.KEY_1):
            self._selection = 0
        elif pyxel.btnp(pyxel.KEY_2):
            self._selection = 1
        elif pyxel.btnp(pyxel.KEY_3):
            self._selection = 2
        elif pyxel.btnp(pyxel.KEY_4):
            self._selection = 3

        self._append_text()

        if inp.confirm:
            ok = self._commit_answer()
            if ok:
                self._audio.play("ui_confirm")
            if ok and self._q_index >= len(self._questions):
                prompt = " / ".join(self._answers)
                return SceneChange("loading", {"prompt": prompt})
        return None

    def draw(self) -> None:
        pyxel.cls(2)

        # Big boss at the top, writhing while asking questions.
        state = (pyxel.frame_count // 20) % 2
        img, bw, bh = boss_sprite(state=state)
        scale = 3
        wobble_y = int(math.sin(pyxel.frame_count * 0.10) * 6)
        wobble_x = int(math.sin(pyxel.frame_count * 0.07) * 4)
        x = WIDTH // 2 - (bw * scale) // 2 + wobble_x
        y = 0 + wobble_y
        pyxel.blt(x, y, img, 0, 0, bw, bh, colkey=0, scale=scale)

        y = 38
        for line in self._guardian_lines:
            self._utext.blit(40, y, line, 7)
            y += 26

        panel_x = 30
        panel_y = 150
        panel_w = WIDTH - 60
        panel_h = HEIGHT - 200
        pyxel.rect(panel_x, panel_y, panel_w, panel_h, 0)
        pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 4)

        q = self._questions[self._q_index]
        self._utext.blit(panel_x + 10, panel_y + 10, f"Q{self._q_index+1}. {q.prompt}", 7)

        base_y = panel_y + 80
        for idx in range(3):
            selected = self._selection == idx
            color = 10 if selected else 7
            self._utext.blit(panel_x + 24, base_y + idx * 34, f"{idx+1}. {q.options[idx]}", color)

        selected = self._selection == 3
        color = 10 if selected else 7
        self._utext.blit(panel_x + 24, base_y + 3 * 34, "4. 自由記述:", color)

        box_x = panel_x + 160
        box_y = base_y + 3 * 34 - 4
        box_w = panel_w - 190
        box_h = 28
        pyxel.rect(box_x, box_y, box_w, box_h, 1)
        pyxel.rectb(box_x, box_y, box_w, box_h, 13)
        typed = self._free_text or "（ここに入力）"
        self._utext.blit(box_x + 8, box_y + 6, typed, 6)

        pyxel.text(panel_x + 18, panel_y + panel_h - 26, "Up/Down or 1-4, Enter/Space confirm, Esc back", 5)
