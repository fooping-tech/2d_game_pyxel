from __future__ import annotations

import colorsys
import hashlib
import random
from dataclasses import dataclass


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha256(text.strip().encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _hsv_to_rgb255(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


_PYXEL_PALETTE: list[tuple[int, int, int]] = [
    (0, 0, 0),
    (29, 43, 83),
    (126, 37, 83),
    (0, 135, 81),
    (171, 82, 54),
    (95, 87, 79),
    (194, 195, 199),
    (255, 241, 232),
    (255, 0, 77),
    (255, 163, 0),
    (255, 236, 39),
    (0, 228, 54),
    (41, 173, 255),
    (131, 118, 156),
    (255, 119, 168),
    (255, 204, 170),
]


def _nearest_pyxel_color(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    best = 0
    best_d = 10**18
    for idx, (pr, pg, pb) in enumerate(_PYXEL_PALETTE):
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best_d:
            best_d = d
            best = idx
    return best


@dataclass(frozen=True)
class Theme:
    prompt: str
    seed: int
    bg: int
    fg: int
    accent: int
    danger: int
    shape_style: str
    item_names: dict[str, str]


def build_theme(prompt: str) -> Theme:
    seed = _seed_from_text(prompt)
    rng = random.Random(seed)

    base_h = rng.random()
    bg_rgb = _hsv_to_rgb255(base_h, 0.35, 0.12)
    fg_rgb = _hsv_to_rgb255((base_h + 0.08) % 1.0, 0.30, 0.82)
    accent_rgb = _hsv_to_rgb255((base_h + 0.52) % 1.0, 0.70, 0.92)
    danger_rgb = _hsv_to_rgb255((base_h + 0.95) % 1.0, 0.85, 0.92)

    shape_style = rng.choice(["round", "blocky", "spiky"])

    vocab = [
        "魔導",
        "蒸気",
        "海底",
        "古代",
        "砂漠",
        "夜会",
        "蛍光",
        "毒霧",
        "お菓子",
        "機械",
    ]
    word = rng.choice(vocab)
    item_names = {
        "speed": f"{word}の脚",
        "jump": f"{word}の跳躍",
        "phase": f"{word}の虚ろ",
        "invuln": f"{word}の護り",
        "hp": f"{word}の心臓",
    }

    return Theme(
        prompt=prompt,
        seed=seed,
        bg=_nearest_pyxel_color(bg_rgb),
        fg=_nearest_pyxel_color(fg_rgb),
        accent=_nearest_pyxel_color(accent_rgb),
        danger=_nearest_pyxel_color(danger_rgb),
        shape_style=shape_style,
        item_names=item_names,
    )

