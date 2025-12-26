from __future__ import annotations

from dataclasses import dataclass

import pyxel

from game.geom import Rect
from game.pixel_art import item_sprite


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
        img, sw, sh = item_sprite(kind=self.kind, col=color)
        scale = max(1, min(r.w // sw, r.h // sh))
        pyxel.blt(x, y, img, 0, 0, sw, sh, colkey=0, scale=scale)
