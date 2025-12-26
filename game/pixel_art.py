from __future__ import annotations

from functools import lru_cache

import pyxel


def _pset_safe(img: pyxel.Image, x: int, y: int, col: int) -> None:
    if 0 <= x < img.width and 0 <= y < img.height:
        img.pset(x, y, col)


@lru_cache(maxsize=64)
def zone_tile(*, zone_index: int, bg: int, dot: int, accent: int, size: int = 32) -> pyxel.Image:
    """
    A scrolling background tile. This is intentionally tiny pixel art that looks good when tiled.
    """
    img = pyxel.Image(size, size)
    img.cls(bg)
    k = max(1, size // 32)

    # Pale versions for objects
    obj_fill = dot
    obj_edge = 7
    obj_accent = accent if accent != 0 else dot

    # Dots / dither to keep it pale but textured.
    for y in range(0, size, 2 * k):
        for x in range(((y // (2 * k)) % 2) * k, size, 4 * k):
            _pset_safe(img, x, y, dot)

    # Zone-specific stamp patterns (small and tile-friendly).
    if zone_index == 0:
        # Beach waves
        for y in range(6 * k, size, 10 * k):
            for x in range(0, size, 4 * k):
                if ((x // k) + (y // k)) % 8 == 0:
                    _pset_safe(img, x, y, obj_edge)
    elif zone_index == 1:
        # Road: dark asphalt band + dashed line
        img.rect(size // 2 - 7 * k, 0, 14 * k, size, obj_fill)
        for y in range(0, size, 8 * k):
            img.rect(size // 2 - 1 * k, y, 2 * k, 4 * k, obj_edge)
    elif zone_index == 2:
        # Village: tiny house
        img.rect(4 * k, size - 14 * k, 12 * k, 8 * k, obj_fill)
        img.tri(3 * k, size - 14 * k, 10 * k, size - 22 * k, 17 * k, size - 14 * k, obj_edge)
        img.rect(9 * k, size - 10 * k, 3 * k, 4 * k, 1)
    elif zone_index == 3:
        # Town: windows
        for x in range(4 * k, size, 10 * k):
            img.rect(x, size - 22 * k, 7 * k, 18 * k, obj_fill)
            _pset_safe(img, x + 2 * k, size - 16 * k, obj_edge)
            _pset_safe(img, x + 4 * k, size - 12 * k, obj_edge)
    elif zone_index == 4:
        # Mountain triangles
        img.tri(0, size, size // 2, 10 * k, size, size, obj_fill)
        img.tri(6 * k, size, size // 2, 16 * k, size - 6 * k, size, obj_edge)
    elif zone_index == 5:
        # Fuji silhouette + snow cap
        img.tri(0, size, size // 2, 4 * k, size, size, obj_fill)
        img.tri(8 * k, size, size // 2, 12 * k, size - 8 * k, size, obj_edge)
        img.tri(size // 2 - 6 * k, 12 * k, size // 2, 4 * k, size // 2 + 6 * k, 12 * k, 7)
    elif zone_index == 6:
        # Sky clouds
        img.circ(10 * k, 12 * k, 6 * k, 7)
        img.circ(18 * k, 14 * k, 5 * k, 7)
        img.rect(6 * k, 14 * k, 18 * k, 6 * k, 7)
    elif zone_index == 7:
        # Space stars
        for i in range(24):
            _pset_safe(img, (i * 13) % size, (i * 7) % size, 7 if i % 3 == 0 else dot)
    elif zone_index == 8:
        # Moon craters
        img.circb(10 * k, 14 * k, 6 * k, obj_fill)
        img.circb(22 * k, 22 * k, 5 * k, obj_edge)
    elif zone_index == 9:
        # Mars dust + rock
        img.rect(0, size - 10 * k, size, 10 * k, obj_fill)
        img.circ(10 * k, size - 7 * k, 4 * k, obj_edge)
    else:
        # Heaven beams
        for x in range(0, size, 8 * k):
            img.rect(x, 0, 2 * k, size, obj_fill)
        img.circb(size // 2, 8 * k, 6 * k, obj_edge)

    # Extra pale overlay: sparse white dots
    for y in range(0, size, 3 * k):
        for x in range((y // (3 * k)) % 3 * k, size, 6 * k):
            _pset_safe(img, x, y, 7)

    return img


@lru_cache(maxsize=32)
def platform_tile(*, fill: int, outline: int = 1, size: int = 8) -> pyxel.Image:
    img = pyxel.Image(size, size)
    img.cls(0)
    img.rect(0, 0, size, size, fill)
    # pixel border
    img.rectb(0, 0, size, size, outline)
    # inner speckles
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            if (x + y) % 7 == 0:
                _pset_safe(img, x, y, 7)
    return img


@lru_cache(maxsize=128)
def enemy_sprite(*, kind: str, state: int, fill: int, danger: int) -> tuple[pyxel.Image, int, int]:
    """
    Returns (image, w, h). Color 0 is transparent.
    """
    if kind == "giant":
        w, h = 32, 22
    else:
        w, h = 16, 14

    img = pyxel.Image(w, h)
    img.cls(0)
    outline = 1
    base = danger if (kind == "spiker" and state == 1) else fill

    img.rect(1, 1, w - 2, h - 2, base)
    img.rectb(1, 1, w - 2, h - 2, outline)

    # Simple faces
    cx = w // 2
    img.pset(cx - 3, 5, outline)
    img.pset(cx + 3, 5, outline)
    img.line(cx - 2, 9, cx + 2, 9, outline)

    if kind == "flyer":
        img.tri(0, h // 2, 4, 3, 4, h - 3, base)
        img.tri(w, h // 2, w - 4, 3, w - 4, h - 3, base)
    elif kind == "jumper":
        img.rect(2, h - 3, w - 4, 2, 7)
    elif kind == "spiker" and state == 1:
        for x in range(3, w - 3, 4):
            img.tri(x, 0, x - 2, 4, x + 2, 4, danger)
    elif kind == "giant":
        img.rect(3, h - 4, w - 6, 3, 7)

    return img, w, h


@lru_cache(maxsize=64)
def item_sprite(*, kind: str, col: int) -> tuple[pyxel.Image, int, int]:
    w, h = 8, 8
    img = pyxel.Image(w, h)
    img.cls(0)
    outline = 1
    img.rect(1, 1, w - 2, h - 2, col)
    img.rectb(1, 1, w - 2, h - 2, outline)
    # Symbol pixel
    if kind == "speed":
        img.line(2, 4, 5, 4, 7)
    elif kind == "jump":
        img.tri(4, 2, 2, 5, 6, 5, 7)
    elif kind == "phase":
        img.pset(3, 3, 7)
        img.pset(4, 4, 7)
    elif kind == "invuln":
        img.circb(4, 4, 2, 7)
    else:
        img.pset(4, 4, 7)
    return img, w, h


@lru_cache(maxsize=16)
def boss_sprite(*, state: int, fill: int = 2, accent: int = 8) -> tuple[pyxel.Image, int, int]:
    """
    Big demon-like boss sprite for the selection scene.
    Color 0 is transparent.
    """
    w, h = 64, 48
    img = pyxel.Image(w, h)
    img.cls(0)
    outline = 1

    # Body mass
    img.rect(10, 10, 44, 28, fill)
    img.circ(10, 24, 14, fill)
    img.circ(54, 24, 14, fill)
    img.rect(10, 22, 44, 18, fill)
    img.rectb(8, 10, 48, 32, outline)

    # Horns
    img.tri(16, 6, 6, 0, 20, 16, accent)
    img.tri(48, 6, 58, 0, 44, 16, accent)
    img.tri(16, 8, 8, 2, 18, 16, outline)
    img.tri(48, 8, 56, 2, 46, 16, outline)

    # Eyes
    img.rect(20, 20, 8, 4, 7)
    img.rect(36, 20, 8, 4, 7)
    img.pset(24, 22, outline)
    img.pset(40, 22, outline)

    # Mouth (state toggles)
    if state == 0:
        img.line(24, 30, 40, 30, outline)
        img.tri(28, 30, 30, 34, 32, 30, 7)
        img.tri(34, 30, 36, 34, 38, 30, 7)
    else:
        img.rect(26, 30, 14, 8, 7)
        img.rectb(26, 30, 14, 8, outline)
        img.tri(28, 30, 30, 34, 32, 30, outline)
        img.tri(34, 30, 36, 34, 38, 30, outline)

    # Small wobble tentacles at bottom
    for i, x in enumerate(range(14, 52, 6)):
        off = (i + state) % 2
        img.line(x, 40, x - 2 + off, 46, accent)
        img.line(x + 1, 40, x + 3 + off, 46, accent)

    return img, w, h
