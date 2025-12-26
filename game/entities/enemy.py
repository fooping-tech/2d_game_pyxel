from __future__ import annotations

import math
from dataclasses import dataclass

import pyxel

from game.geom import Rect
from game.pixel_art import enemy_sprite
from game.util import clamp


@dataclass
class Enemy:
    kind: str
    rect: Rect
    vx: float
    vy: float
    alive: bool = True
    can_stomp: bool = True

    t: float = 0.0
    state: int = 0

    def update(self, dt: float) -> None:
        self.t += dt
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

    def draw(self, cam_x: float, cam_y: float, color: int, danger: int) -> None:
        if not self.alive:
            return
        r = self.rect
        x = int(r.x - cam_x)
        y = int(r.y - cam_y)
        img, sw, sh = enemy_sprite(kind=self.kind, state=self.state, fill=color, danger=danger)
        scale = max(1, min(r.w // sw, r.h // sh))
        pyxel.blt(x, y, img, 0, 0, sw, sh, colkey=0, scale=scale)


def make_walker(x: int, y: int) -> Enemy:
    return Enemy(kind="walker", rect=Rect(x, y, 42, 34), vx=70, vy=0, can_stomp=True)


def make_flyer(x: int, y: int) -> Enemy:
    return Enemy(kind="flyer", rect=Rect(x, y, 46, 30), vx=110, vy=0, can_stomp=True)


def make_jumper(x: int, y: int) -> Enemy:
    return Enemy(kind="jumper", rect=Rect(x, y, 40, 36), vx=0, vy=0, can_stomp=True)


def make_spiker(x: int, y: int) -> Enemy:
    return Enemy(kind="spiker", rect=Rect(x, y, 46, 40), vx=0, vy=0, can_stomp=True)


def make_giant(x: int, y: int) -> Enemy:
    return Enemy(kind="giant", rect=Rect(x, y, 130, 90), vx=40, vy=0, can_stomp=False)


def update_enemy_behavior(enemy: Enemy, dt: float, world_bounds_x: tuple[int, int]) -> None:
    if not enemy.alive:
        return
    left_x, right_x = world_bounds_x
    r = enemy.rect

    if enemy.kind == "walker":
        if r.left < left_x or r.right > right_x:
            enemy.vx *= -1
            r.x = max(left_x, min(r.x, right_x - r.w))
    elif enemy.kind == "flyer":
        enemy.vy = 70.0 * math.sin(enemy.t * 2.3)
        if r.left < left_x or r.right > right_x:
            enemy.vx *= -1
        enemy.vx = clamp(enemy.vx, -150, 150)
    elif enemy.kind == "jumper":
        if enemy.t - int(enemy.t) < dt and enemy.state == 0:
            enemy.state = 1
            enemy.vy = -680
        enemy.vy += 1800 * dt
    elif enemy.kind == "spiker":
        period = 1.8
        phase = (enemy.t % period) / period
        enemy.state = 1 if phase > 0.62 else 0
    elif enemy.kind == "giant":
        if r.left < left_x or r.right > right_x:
            enemy.vx *= -1
            r.x = max(left_x, min(r.x, right_x - r.w))
