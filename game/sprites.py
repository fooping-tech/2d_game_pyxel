from __future__ import annotations

from functools import lru_cache

import pyxel


SPR_W = 17
SPR_H = 22


@lru_cache(maxsize=256)
def character_sprite(
    *,
    body_color: int,
    shape_style: str,
    eye_style: str,
    mouth_style: str,
    hat_style: str,
    pose: str = "stand",
) -> pyxel.Image:
    """
    Build a small pixel-art sprite (SPR_W x SPR_H) and return it.
    Color 0 is treated as transparent (colkey=0 for blt), so outlines avoid using 0.
    """
    img = pyxel.Image(SPR_W, SPR_H)
    img.cls(0)

    # Use dark-blue as outline (not 0), and white for highlights.
    outline = 1
    hi = 7

    def pset(x: int, y: int, c: int) -> None:
        if 0 <= x < SPR_W and 0 <= y < SPR_H:
            img.pset(x, y, c)

    def rect(x: int, y: int, w: int, h: int, c: int) -> None:
        img.rect(x, y, w, h, c)

    # --- Body silhouette (pixel-art) ---
    # We draw a compact character that scales cleanly to 34x44 (scale=2).
    crouch = pose == "crouch"
    if shape_style == "round":
        # Rounded blob (shifted down so feet reach the last row)
        if crouch:
            rect(4, 8, 9, 11, body_color)
            rect(5, 7, 7, 13, body_color)
            rect(6, 6, 5, 15, body_color)
        else:
            rect(4, 6, 9, 14, body_color)
            rect(5, 5, 7, 16, body_color)
            rect(6, 4, 5, 18, body_color)
    elif shape_style == "spiky":
        # Diamond/spiky
        top = 6 if not crouch else 8
        peak = 8 if not crouch else 7
        for dy in range(peak + 1):
            rect(8 - dy, top + dy, 1 + dy * 2, 1, body_color)
        bottom_start = top + peak + 1
        for dy in range(SPR_H - bottom_start):
            rect(1 + dy, bottom_start + dy, 15 - dy * 2, 1, body_color)
    else:
        # Blocky with tiny head notch
        if crouch:
            rect(4, 8, 9, 12, body_color)
            rect(5, 7, 7, 1, body_color)
        else:
            rect(4, 6, 9, 16, body_color)
            rect(5, 5, 7, 1, body_color)

    # Simple shading/highlight dither
    for y in range(4, SPR_H - 1):
        for x in range(0, SPR_W):
            if img.pget(x, y) != body_color:
                continue
            if (x + y) % 7 == 0 and x >= 10:
                pset(x, y, hi)

    # Outline (4-neighborhood) to look more like pixel art
    for y in range(SPR_H):
        for x in range(SPR_W):
            if img.pget(x, y) != body_color and img.pget(x, y) != hi:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < SPR_W and 0 <= ny < SPR_H and img.pget(nx, ny) == 0:
                    pset(nx, ny, outline)

    # Ensure the feet touch the bottom row (avoid "floating" look after scaling).
    for x in range(SPR_W):
        if img.pget(x, SPR_H - 2) in (body_color, hi) and img.pget(x, SPR_H - 1) == 0:
            pset(x, SPR_H - 1, body_color)

    # --- Face ---
    face_col = outline
    cx = SPR_W // 2
    eye_y = 10
    eye_dx = 3

    if eye_style == "sleepy":
        img.line(cx - eye_dx - 2, eye_y, cx - eye_dx + 2, eye_y, face_col)
        img.line(cx + eye_dx - 2, eye_y, cx + eye_dx + 2, eye_y, face_col)
    else:
        pset(cx - eye_dx, eye_y, face_col)
        pset(cx + eye_dx, eye_y, face_col)
        if eye_style == "angry":
            pset(cx - eye_dx - 1, eye_y - 1, face_col)
            pset(cx + eye_dx + 1, eye_y - 1, face_col)

    mouth_y = 14
    if mouth_style == "flat":
        img.line(cx - 3, mouth_y, cx + 3, mouth_y, face_col)
    elif mouth_style == "fang":
        img.line(cx - 3, mouth_y, cx + 3, mouth_y, face_col)
        pset(cx, mouth_y + 1, face_col)
    else:
        pset(cx - 2, mouth_y, face_col)
        pset(cx - 1, mouth_y + 1, face_col)
        pset(cx, mouth_y + 1, face_col)
        pset(cx + 1, mouth_y + 1, face_col)
        pset(cx + 2, mouth_y, face_col)

    # --- Hat ---
    if hat_style == "triangle":
        pset(cx, 1, face_col)
        img.line(cx - 2, 3, cx + 2, 3, face_col)
        img.tri(cx, 1, cx - 4, 4, cx + 4, 4, hi)
    elif hat_style == "halo":
        img.circb(cx, 2, 3, 10)

    return img
