from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pyxel

from game.util import clamp


@dataclass
class ScreenShake:
    time_left: float = 0.0
    strength: float = 0.0

    def kick(self, strength: float, seconds: float) -> None:
        self.strength = max(self.strength, strength)
        self.time_left = max(self.time_left, seconds)

    def update(self, dt: float) -> None:
        self.time_left = max(0.0, self.time_left - dt)
        self.strength = clamp(self.strength - dt * 22.0, 0.0, 9999.0)

    def offset(self, rng: random.Random) -> tuple[int, int]:
        if self.time_left <= 0.0 or self.strength <= 0.0:
            return 0, 0
        s = self.strength
        return int(rng.uniform(-s, s)), int(rng.uniform(-s, s))


@dataclass
class HitStop:
    frames_left: int = 0

    def trigger(self, frames: int) -> None:
        self.frames_left = max(self.frames_left, frames)

    def consume_frame(self) -> bool:
        if self.frames_left <= 0:
            return False
        self.frames_left -= 1
        return True


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    color: int
    life: float


class ParticleSystem:
    def __init__(self) -> None:
        self._particles: list[Particle] = []

    def burst(self, pos: tuple[float, float], color: int, count: int = 14, speed: float = 520.0) -> None:
        ox, oy = pos
        for _ in range(count):
            angle = random.random() * math.tau
            mag = speed * (0.35 + random.random() * 0.85)
            vx = math.cos(angle) * mag
            vy = math.sin(angle) * mag
            self._particles.append(
                Particle(
                    x=ox,
                    y=oy,
                    vx=vx,
                    vy=vy,
                    radius=2.0 + random.random() * 3.0,
                    color=color,
                    life=0.45 + random.random() * 0.35,
                )
            )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += 1600.0 * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.radius = max(0.0, p.radius - dt * 6.0)
            alive.append(p)
        self._particles = alive

    def draw(self, cam_x: float, cam_y: float) -> None:
        for p in self._particles:
            if p.radius <= 0.5:
                continue
            x = int(p.x - cam_x)
            y = int(p.y - cam_y)
            pyxel.circ(x, y, int(p.radius), p.color)

