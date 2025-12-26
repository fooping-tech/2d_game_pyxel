from __future__ import annotations

import pyxel

from game.audio import AudioManager
from game.character import CharacterSpec
from game.config import GameConfig
from game.constants import HEIGHT, WIDTH
from game.scenes.base import SceneChange
from game.theme import build_theme
from game.unicode_text import UnicodeText
from game.sprites import SPR_H, SPR_W, character_sprite


class IntroScene:
    name = "intro"

    def __init__(self, audio: AudioManager, utext: UnicodeText, cfg: GameConfig) -> None:
        self._audio = audio
        self._utext = utext
        self._cfg = cfg
        self._t_left = 0.0
        self._payload: dict = {}
        self._character = CharacterSpec.from_seed(0)
        self._shape_style = "blocky"
        self._body_color = 12

    def enter(self, payload: dict) -> None:
        self._payload = payload
        prompt = str(payload.get("prompt", ""))
        theme = build_theme(prompt or "default")
        self._shape_style = theme.shape_style
        self._body_color = theme.accent
        ch = payload.get("character")
        if isinstance(ch, dict):
            self._character = CharacterSpec.from_dict(ch)
        else:
            self._character = CharacterSpec.from_seed(0)
        self._t_left = 5.0
        self._audio.play_bgm("intro")
        self._audio.play("ui_confirm")

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]
        self._t_left = max(0.0, self._t_left - dt)
        if inp.confirm or self._t_left <= 0.0:
            return SceneChange("play", dict(self._payload))
        if inp.back:
            return SceneChange("title", {})
        return None

    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.rect(0, 0, WIDTH, HEIGHT, 0)

        # Frame
        pyxel.rect(40, 60, WIDTH - 80, HEIGHT - 120, 1)
        pyxel.rectb(40, 60, WIDTH - 80, HEIGHT - 120, 5)

        title = "READY"
        spr = self._utext.render(title, 10, self._cfg.title_font_px_big)
        self._utext.blit(WIDTH // 2 - spr.w // 2, 78, title, 10, size_px=self._cfg.title_font_px_big)

        prompt = str(self._payload.get("prompt", ""))[:60]
        if prompt:
            sp = self._utext.render(prompt, 6)
            self._utext.blit(WIDTH // 2 - sp.w // 2, 128, prompt, 6)

        ch = self._character.effective()

        # Left: character portrait
        _draw_portrait(
            x=120,
            y=190,
            w=280,
            h=340,
            body_color=self._body_color,
            shape_style=self._shape_style,
            character=ch,
        )

        # Right: radar chart
        radar_cx = 700
        radar_cy = 320
        r = 120
        axes = [
            ("MOVE", ch.speed_mult, 0.78, 1.22),
            ("JUMP", ch.jump_mult, 0.78, 1.22),
            ("CHARGE", ch.charge_mult, 0.78, 1.22),
            ("HP", float(ch.base_hp), 2.0, 5.0),
            ("FLOAT", 1.0 / max(0.10, ch.gravity_mult), 0.78, 1.22),
        ]
        _draw_radar(radar_cx, radar_cy, r, axes, utext=self._utext)

        # Numbers
        rows = [
            ("MOVE", f"x{ch.speed_mult:.2f}"),
            ("JUMP", f"x{ch.jump_mult:.2f}"),
            ("CHARGE", f"x{ch.charge_mult:.2f}"),
            ("HP", f"{ch.base_hp:d}"),
            ("GRAVITY", f"x{ch.gravity_mult:.2f}"),
        ]
        tx = 560
        ty = 430
        for name, val in rows:
            self._utext.blit(tx, ty, f"{name:7s} {val}", 6)
            ty += 22

        hint = "Enter/Space: start   Esc: title"
        sh = self._utext.render(hint, 6)
        self._utext.blit(WIDTH // 2 - sh.w // 2, HEIGHT - 90, hint, 6)


def _draw_portrait(
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    body_color: int,
    shape_style: str,
    character: CharacterSpec,
) -> None:
    spr = character_sprite(
        body_color=body_color,
        shape_style=shape_style,
        eye_style=character.eye_style,
        mouth_style=character.mouth_style,
        hat_style=character.hat_style,
        pose="stand",
    )
    # Scale as large as possible while preserving pixel look.
    scale = max(1, min(w // SPR_W, h // SPR_H))
    dw = SPR_W * scale
    dh = SPR_H * scale
    dx = x + w // 2 - dw // 2
    dy = y + h // 2 - dh // 2
    pyxel.blt(dx, dy, spr, 0, 0, SPR_W, SPR_H, colkey=0, scale=scale)


def _draw_radar(
    cx: int,
    cy: int,
    radius: int,
    axes: list[tuple[str, float, float, float]],
    *,
    utext: UnicodeText,
) -> None:
    import math

    n = len(axes)
    if n <= 2:
        return
    angles = [(-math.pi / 2) + i * (2 * math.pi / n) for i in range(n)]

    # Grid
    for g in (0.25, 0.5, 0.75, 1.0):
        pts: list[tuple[int, int]] = []
        rr = int(radius * g)
        for a in angles:
            pts.append((cx + int(math.cos(a) * rr), cy + int(math.sin(a) * rr)))
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            pyxel.line(x1, y1, x2, y2, 5)

    for a in angles:
        pyxel.line(cx, cy, cx + int(math.cos(a) * radius), cy + int(math.sin(a) * radius), 13)

    # Values polygon (fan fill)
    vals: list[tuple[int, int]] = []
    for (label, v, vmin, vmax), a in zip(axes, angles):
        if vmax <= vmin:
            t = 0.0
        else:
            t = (v - vmin) / (vmax - vmin)
        t = max(0.0, min(1.0, t))
        rr = int(radius * (0.20 + 0.80 * t))
        vals.append((cx + int(math.cos(a) * rr), cy + int(math.sin(a) * rr)))

    for i in range(n):
        x1, y1 = vals[i]
        x2, y2 = vals[(i + 1) % n]
        pyxel.tri(cx, cy, x1, y1, x2, y2, 12)
    for i in range(n):
        x1, y1 = vals[i]
        x2, y2 = vals[(i + 1) % n]
        pyxel.line(x1, y1, x2, y2, 7)

    # Labels
    for (label, _, _, _), a in zip(axes, angles):
        lx = cx + int(math.cos(a) * (radius + 30))
        ly = cy + int(math.sin(a) * (radius + 30))
        spr = utext.render(label, 7)
        utext.blit(lx - spr.w // 2, ly - spr.h // 2, label, 7)
