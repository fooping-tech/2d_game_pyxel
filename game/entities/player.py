from __future__ import annotations

from dataclasses import dataclass

import pyxel

from game.constants import (
    INVULN_SECONDS_ON_HIT,
    JUMP_CHARGE_SECONDS,
    JUMP_MAX_VY,
    JUMP_MIN_VY,
    PLAYER_H,
    PLAYER_MAX_X_SPEED,
    PLAYER_W,
    PLAYER_X_ACCEL,
    PLAYER_X_FRICTION,
)
from game.geom import Rect
from game.util import clamp, lerp


@dataclass
class Player:
    x: float
    y: float
    vx: float
    vy: float
    grounded: bool = False

    hp: int = 3
    max_hp: int = 3
    invuln: float = 0.0

    charge: float = 0.0

    trait_speed_mult: float = 1.0
    trait_jump_mult: float = 1.0
    trait_charge_mult: float = 1.0

    speed_boost: float = 0.0
    jump_boost: float = 0.0
    phase: float = 0.0
    invuln_item: float = 0.0

    def rect(self) -> Rect:
        return Rect(int(self.x), int(self.y), PLAYER_W, PLAYER_H)

    def is_invulnerable(self) -> bool:
        return self.invuln > 0.0 or self.invuln_item > 0.0

    def can_phase(self) -> bool:
        return self.phase > 0.0

    def x_speed_mult(self) -> float:
        boost = 1.55 if self.speed_boost > 0.0 else 1.0
        return self.trait_speed_mult * boost

    def jump_mult(self) -> float:
        boost = 1.45 if self.jump_boost > 0.0 else 1.0
        return self.trait_jump_mult * boost

    def update_timers(self, dt: float) -> None:
        self.invuln = max(0.0, self.invuln - dt)
        self.speed_boost = max(0.0, self.speed_boost - dt)
        self.jump_boost = max(0.0, self.jump_boost - dt)
        self.phase = max(0.0, self.phase - dt)
        self.invuln_item = max(0.0, self.invuln_item - dt)

    def apply_damage(self, amount: int) -> bool:
        if self.is_invulnerable():
            return False
        self.hp = max(0, self.hp - amount)
        self.invuln = INVULN_SECONDS_ON_HIT
        return True

    def heal_max_hp(self, amount: int, cap: int = 8) -> None:
        self.max_hp = min(cap, self.max_hp + amount)
        self.hp = min(self.max_hp, self.hp + amount)

    def update_horizontal(self, dt: float, left: bool, right: bool) -> None:
        target = 0.0
        if left and not right:
            target = -1.0
        elif right and not left:
            target = 1.0

        accel = PLAYER_X_ACCEL * self.x_speed_mult()
        if target != 0.0:
            self.vx += target * accel * dt
        else:
            if self.vx > 0:
                self.vx = max(0.0, self.vx - PLAYER_X_FRICTION * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + PLAYER_X_FRICTION * dt)

        max_speed = PLAYER_MAX_X_SPEED * self.x_speed_mult()
        self.vx = clamp(self.vx, -max_speed, max_speed)

    def update_jump_charge(self, dt: float, jump_down: bool, jump_released: bool) -> bool:
        if self.grounded and jump_down:
            self.charge = clamp(self.charge + (dt * self.trait_charge_mult) / JUMP_CHARGE_SECONDS, 0.0, 1.0)
        if self.grounded and jump_released:
            power = lerp(JUMP_MIN_VY, JUMP_MAX_VY, self.charge) * self.jump_mult()
            self.vy = -power
            self.grounded = False
            self.charge = 0.0
            return True
        if not jump_down and self.charge > 0.0 and not self.grounded:
            self.charge = 0.0
        return False

    def draw(self, cam_x: float, cam_y: float, theme_color: int, style: str) -> None:
        r = self.rect()
        x = int(r.x - cam_x)
        y = int(r.y - cam_y)

        if self.is_invulnerable() and (pyxel.frame_count // 5) % 2 == 0:
            return

        if style == "round":
            pyxel.circ(x + r.w // 2, y + r.h // 2, min(r.w, r.h) // 2, theme_color)
        elif style == "spiky":
            cx = x + r.w // 2
            cy = y + r.h // 2
            pyxel.tri(cx, y, x + r.w, cy, cx, y + r.h, theme_color)
            pyxel.tri(cx, y, x, cy, cx, y + r.h, theme_color)
        else:
            pyxel.rect(x, y, r.w, r.h, theme_color)

    def draw_face(self, cam_x: float, cam_y: float, eye_style: str, mouth_style: str, hat_style: str) -> None:
        r = self.rect()
        x = int(r.x - cam_x)
        y = int(r.y - cam_y)
        if r.w < 10 or r.h < 10:
            return

        cx = x + r.w // 2
        eye_y = y + int(r.h * 0.35)
        eye_dx = int(r.w * 0.18)
        col = 0

        if eye_style == "sleepy":
            pyxel.line(cx - eye_dx - 5, eye_y, cx - eye_dx + 5, eye_y, col)
            pyxel.line(cx + eye_dx - 5, eye_y, cx + eye_dx + 5, eye_y, col)
        else:
            pyxel.circ(cx - eye_dx, eye_y, 1, col)
            pyxel.circ(cx + eye_dx, eye_y, 1, col)
            if eye_style == "angry":
                pyxel.line(cx - eye_dx - 7, eye_y - 5, cx - eye_dx + 5, eye_y - 2, col)
                pyxel.line(cx + eye_dx - 5, eye_y - 2, cx + eye_dx + 7, eye_y - 5, col)

        mouth_y = y + int(r.h * 0.64)
        if mouth_style == "flat":
            pyxel.line(cx - 7, mouth_y, cx + 7, mouth_y, col)
        elif mouth_style == "fang":
            pyxel.line(cx - 8, mouth_y, cx + 8, mouth_y, col)
            pyxel.tri(cx - 1, mouth_y, cx + 1, mouth_y, cx, mouth_y + 4, col)
        else:
            pyxel.line(cx - 6, mouth_y, cx + 6, mouth_y, col)
            pyxel.pset(cx - 6, mouth_y - 1, col)
            pyxel.pset(cx + 6, mouth_y - 1, col)

        if hat_style == "triangle":
            pyxel.tri(cx, y - 8, cx - 10, y + 6, cx + 10, y + 6, col)
        elif hat_style == "halo":
            pyxel.circb(cx, y - 8, 9, col)
