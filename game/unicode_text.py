from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pyxel

from PIL import Image, ImageDraw, ImageFont  # type: ignore[import-not-found]


def _split_paths(value: str) -> list[str]:
    if not value:
        return []
    sep = ";" if os.name == "nt" else ":"
    return [p.strip() for p in value.split(sep) if p.strip()]


def _candidate_font_paths() -> list[str]:
    paths: list[str] = []

    env_single = os.environ.get("GAME_FONT_PATH", "").strip()
    if env_single:
        paths.append(env_single)

    env_multi = os.environ.get("GAME_FONT_PATHS", "").strip()
    paths.extend(_split_paths(env_multi))

    # macOS
    paths.extend(
        [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
            "/System/Library/Fonts/AppleGothic.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    )

    # Linux (common Noto paths)
    paths.extend(
        [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )

    # Windows (best-effort)
    windir = os.environ.get("WINDIR", "C:\\Windows")
    paths.extend(
        [
            str(Path(windir) / "Fonts" / "msgothic.ttc"),
            str(Path(windir) / "Fonts" / "meiryo.ttc"),
            str(Path(windir) / "Fonts" / "YuGothM.ttc"),
        ]
    )

    uniq: list[str] = []
    seen: set[str] = set()
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        uniq.append(p)
    return uniq


@lru_cache(maxsize=16)
def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in _candidate_font_paths():
        try:
            if Path(p).exists():
                return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


@dataclass(frozen=True)
class TextSprite:
    img: pyxel.Image
    w: int
    h: int


class UnicodeText:
    def __init__(self, *, font_px: int = 14) -> None:
        self.font_px = font_px

    @lru_cache(maxsize=1024)
    def render(self, text: str, color: int, size_px: int | None = None) -> TextSprite:
        if not text:
            img = pyxel.Image(1, 1)
            img.cls(0)
            return TextSprite(img=img, w=0, h=0)

        size = int(size_px) if size_px is not None else self.font_px
        font = _load_font(size)
        dummy = Image.new("L", (1, 1), 0)
        draw = ImageDraw.Draw(dummy)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = max(1, bbox[2] - bbox[0])
        h = max(1, bbox[3] - bbox[1])

        canvas = Image.new("L", (w, h), 0)
        draw2 = ImageDraw.Draw(canvas)
        draw2.text((-bbox[0], -bbox[1]), text, font=font, fill=255)

        px = pyxel.Image(w, h)
        px.cls(0)
        data = canvas.load()
        for y in range(h):
            for x in range(w):
                if data[x, y] > 0:
                    px.pset(x, y, color)
        return TextSprite(img=px, w=w, h=h)

    def blit(self, x: int, y: int, text: str, color: int, *, size_px: int | None = None) -> None:
        spr = self.render(text, color, size_px)
        if spr.w <= 0 or spr.h <= 0:
            return
        pyxel.blt(x, y, spr.img, 0, 0, spr.w, spr.h, colkey=0)
