from __future__ import annotations

from dataclasses import dataclass

import pyxel

from game.geom import Rect


@dataclass
class Item:
    kind: str
    rect: Rect
    taken: bool = False

    def draw(self, cam_x: float, cam_y: float, color: int) -> None:
        if self.taken:
            return
        r = self.rect
        x = int(r.x - cam_x)
        y = int(r.y - cam_y)
        pyxel.rect(x, y, r.w, r.h, color)
