from __future__ import annotations

from dataclasses import dataclass

import pyxel

from game.geom import Rect
from game.pixel_art import platform_tile


@dataclass
class Platform:
    rect: Rect

    def draw(self, cam_x: float, cam_y: float, color: int) -> None:
        r = self.rect
        x = int(r.x - cam_x)
        y = int(r.y - cam_y)
        tile = platform_tile(fill=color, outline=1, size=8)
        ts = 8
        for yy in range(y, y + r.h, ts):
            for xx in range(x, x + r.w, ts):
                pyxel.blt(xx, yy, tile, 0, 0, ts, ts, colkey=0)
