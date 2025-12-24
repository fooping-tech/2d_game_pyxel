from __future__ import annotations

import random

import pyxel

from game.audio import AudioManager
from game.character import CharacterSpec
from game.constants import (
    FLOOR_HEIGHT_PX,
    GRAVITY,
    HEIGHT,
    WATER_BASE_SPEED,
    WATER_SPEED_PER_FLOOR,
    WATER_START_OFFSET,
    WIDTH,
)
from game.effects import HitStop, ParticleSystem, ScreenShake
from game.entities.enemy import (
    Enemy,
    make_flyer,
    make_giant,
    make_jumper,
    make_spiker,
    make_walker,
    update_enemy_behavior,
)
from game.entities.item import Item
from game.entities.platform import Platform
from game.entities.player import Player
from game.geom import Rect
from game.scenes.base import SceneChange
from game.theme import Theme, build_theme
from game.unicode_text import UnicodeText
from game.util import clamp


class PlayScene:
    name = "play"

    def __init__(self, audio: AudioManager, utext: UnicodeText, rng: random.Random) -> None:
        self._audio = audio
        self._utext = utext
        self._rng = rng

        self._theme: Theme = build_theme("default")
        self._player = Player(x=0, y=0, vx=0, vy=0)
        self._platforms: list[Platform] = []
        self._items: list[Item] = []
        self._enemies: list[Enemy] = []

        self._camera_x = 0.0
        self._camera_y = 0.0
        self._start_y = 0.0
        self._min_y = 0.0
        self._floor = 0

        self._water_y = 0.0
        self._shake = ScreenShake()
        self._hitstop = HitStop()
        self._particles = ParticleSystem()

        self._spawn_top_y = 0.0
        self._reason = "defeated"
        self._was_grounded = False
        self._last_water_warn_frame = -10**9
        self._character = CharacterSpec.from_seed(0)

    def enter(self, payload: dict) -> None:
        prompt = str(payload.get("prompt", ""))
        self._theme = build_theme(prompt or "default")
        self._rng.seed(self._theme.seed)
        ch = payload.get("character")
        if isinstance(ch, dict):
            self._character = CharacterSpec.from_dict(ch)
        else:
            self._character = CharacterSpec.from_seed(self._theme.seed)

        self._start_y = 320.0
        self._player = Player(x=WIDTH / 2 - 16, y=self._start_y, vx=0, vy=0)
        self._player.hp = 3
        self._player.max_hp = 3

        self._platforms = []
        self._items = []
        self._enemies = []
        self._particles = ParticleSystem()
        self._shake = ScreenShake()
        self._hitstop = HitStop()

        self._min_y = self._player.y
        self._floor = 0

        ground = Platform(Rect(40, int(self._start_y + 90), WIDTH - 80, 26))
        self._platforms.append(ground)

        self._spawn_top_y = self._start_y + 90
        self._water_y = self._start_y + WATER_START_OFFSET
        self._reason = "defeated"
        self._was_grounded = True
        self._last_water_warn_frame = -10**9

        for _ in range(24):
            self._spawn_more()

        self._camera_y = self._player.y - HEIGHT * 0.60
        self._camera_x = 0.0

    def _current_floor(self) -> int:
        return max(0, int((self._start_y - self._min_y) / FLOOR_HEIGHT_PX))

    def _spawn_more(self) -> None:
        gap = self._rng.randint(70, 130)
        next_y = self._spawn_top_y - gap
        width = self._rng.randint(120, 240)
        x = self._rng.randint(20, WIDTH - 20 - width)

        plat = Platform(Rect(x, int(next_y), width, 22))
        self._platforms.append(plat)
        self._spawn_top_y = next_y

        if self._rng.random() < 0.22:
            kind = self._rng.choices(
                ["speed", "jump", "phase", "invuln", "hp"],
                weights=[28, 26, 16, 16, 14],
                k=1,
            )[0]
            ir = Rect(plat.rect.centerx - 12, plat.rect.top - 28, 24, 24)
            self._items.append(Item(kind=kind, rect=ir))

        if self._rng.random() < 0.18:
            floor = self._current_floor()
            pool: list[str] = ["walker", "spiker", "flyer", "jumper"]
            weights = [32, 22, 20, 18]
            if floor >= 10:
                pool.append("giant")
                weights.append(8)

            kind = self._rng.choices(pool, weights=weights, k=1)[0]
            ex = plat.rect.centerx - 20
            ey = plat.rect.top - 36
            if kind == "walker":
                self._enemies.append(make_walker(ex, ey))
            elif kind == "spiker":
                self._enemies.append(make_spiker(ex, ey))
            elif kind == "flyer":
                self._enemies.append(make_flyer(ex, ey - 70))
            elif kind == "jumper":
                self._enemies.append(make_jumper(ex, ey))
            else:
                self._enemies.append(make_giant(ex - 40, ey - 30))

    def _apply_item(self, kind: str) -> None:
        if kind == "speed":
            self._player.speed_boost = max(self._player.speed_boost, 6.0)
        elif kind == "jump":
            self._player.jump_boost = max(self._player.jump_boost, 6.0)
        elif kind == "phase":
            self._player.phase = max(self._player.phase, 4.0)
        elif kind == "invuln":
            self._player.invuln_item = max(self._player.invuln_item, 4.0)
        elif kind == "hp":
            self._player.heal_max_hp(1)

    def _stomp_kill(self, enemy: Enemy) -> None:
        enemy.alive = False
        self._audio.play("stomp")
        self._shake.kick(strength=9.0, seconds=0.16)
        self._hitstop.trigger(frames=4)
        self._particles.burst(enemy.rect.center, color=self._theme.accent, count=18, speed=560.0)
        self._player.vy = -540.0 * self._player.jump_mult()

    def _enemy_collisions(self, prev_rect: Rect) -> None:
        if self._player.can_phase():
            return

        pr = self._player.rect()
        for e in self._enemies:
            if not e.alive:
                continue
            if not pr.colliderect(e.rect):
                continue

            falling = self._player.vy > 50.0
            stomp = falling and prev_rect.bottom <= e.rect.top + 6
            if stomp and e.can_stomp:
                if e.kind == "spiker" and e.state == 1:
                    stomp = False
                if stomp:
                    self._stomp_kill(e)
                    return

            took = self._player.apply_damage(1)
            if not took:
                return
            self._audio.play("hit")
            if self._player.hp <= 0:
                self._reason = "hp"
                return

            if pr.centerx < e.rect.centerx:
                self._player.vx = -320
            else:
                self._player.vx = 320
            self._player.vy = -420

    def _platform_collisions(self, prev_rect: Rect) -> None:
        if self._player.can_phase():
            return
        pr = self._player.rect()
        for p in self._platforms:
            if pr.right <= p.rect.left or pr.left >= p.rect.right:
                continue
            if prev_rect.bottom <= p.rect.top + 2 and (p.rect.top - 2) <= pr.bottom <= (p.rect.top + 12):
                self._player.y = p.rect.top - pr.h
                self._player.vy = 0.0
                self._player.grounded = True
                return

    def update(self, dt: float, inp) -> SceneChange | None:  # type: ignore[override]
        if inp.back:
            self._audio.play("ui_confirm")
            self._audio.stop_loop("charge")
            return SceneChange("title", {})

        self._shake.update(dt)
        self._particles.update(dt)

        if self._hitstop.consume_frame():
            return None

        while self._spawn_top_y > self._camera_y - HEIGHT * 2.0:
            self._spawn_more()

        self._player.update_timers(dt)
        self._player.update_horizontal(dt, inp.left, inp.right)

        jumped = self._player.update_jump_charge(dt, inp.jump_down, inp.jump_released)
        if jumped:
            self._audio.stop_loop("charge")
            self._audio.play("jump")
            self._shake.kick(strength=2.0, seconds=0.07)
        else:
            charging = self._player.grounded and inp.jump_down and self._player.charge > 0.02
            if charging:
                self._audio.play_loop("charge", volume=0.8)
            else:
                self._audio.stop_loop("charge")

        prev_rect = self._player.rect()
        self._player.grounded = False

        self._player.vy += GRAVITY * dt
        self._player.x += self._player.vx * dt
        self._player.y += self._player.vy * dt

        if not self._player.can_phase():
            self._player.x = clamp(self._player.x, 0, WIDTH - prev_rect.w)
        else:
            if self._player.x < -prev_rect.w:
                self._player.x = WIDTH - 1
            elif self._player.x > WIDTH:
                self._player.x = -prev_rect.w + 1

        self._platform_collisions(prev_rect)
        self._enemy_collisions(prev_rect)

        if (not self._was_grounded) and self._player.grounded:
            self._audio.play("land")
        self._was_grounded = self._player.grounded

        pr = self._player.rect()
        for item in self._items:
            if item.taken:
                continue
            if pr.colliderect(item.rect):
                item.taken = True
                self._apply_item(item.kind)
                self._audio.play("pickup")
                self._particles.burst(item.rect.center, color=self._theme.accent, count=10, speed=420.0)
        self._items = [i for i in self._items if not i.taken]

        floor = self._current_floor()
        self._floor = max(self._floor, floor)
        self._min_y = min(self._min_y, self._player.y)

        water_speed = WATER_BASE_SPEED + self._floor * WATER_SPEED_PER_FLOOR
        self._water_y -= water_speed * dt
        water_dist = self._water_y - pr.bottom
        if water_dist < 180 and pyxel.frame_count - self._last_water_warn_frame > 55:
            self._audio.play("water_warn")
            self._last_water_warn_frame = pyxel.frame_count
        if pr.bottom > self._water_y:
            self._reason = "water"
            self._audio.stop_loop("charge")
            return SceneChange("game_over", {"floor": self._floor, "reason": self._reason, "prompt": self._theme.prompt})

        if self._player.hp <= 0:
            self._audio.stop_loop("charge")
            return SceneChange("game_over", {"floor": self._floor, "reason": self._reason, "prompt": self._theme.prompt})

        target_cam_y = self._player.y - HEIGHT * 0.60
        self._camera_y = min(self._camera_y, target_cam_y)
        self._camera_x = 0.0

        for e in self._enemies:
            update_enemy_behavior(e, dt, world_bounds_x=(0, WIDTH))
            e.update(dt)
        self._enemies = [e for e in self._enemies if e.alive or (self._camera_y - e.rect.y) < HEIGHT * 3]

        cutoff = self._camera_y + HEIGHT * 2.5
        self._platforms = [p for p in self._platforms if p.rect.y < cutoff]

        if pr.y > self._camera_y + HEIGHT * 1.8:
            self._reason = "fall"
            self._audio.stop_loop("charge")
            return SceneChange("game_over", {"floor": self._floor, "reason": self._reason, "prompt": self._theme.prompt})

        return None

    def _draw_ui(self) -> None:
        pyxel.text(WIDTH - 80, 6, f"FLOOR {self._floor}", self._theme.fg)
        pyxel.text(WIDTH - 80, 18, f"HP {self._player.hp}/{self._player.max_hp}", self._theme.fg)

        water_dist = int(max(0.0, self._water_y - self._player.rect().bottom))
        pyxel.text(WIDTH - 112, 30, f"WATER {water_dist}px", self._theme.fg)

        effects: list[str] = []
        if self._player.speed_boost > 0:
            effects.append("SPD")
        if self._player.jump_boost > 0:
            effects.append("JMP")
        if self._player.phase > 0:
            effects.append("PHASE")
        if self._player.invuln_item > 0:
            effects.append("INV")
        if effects:
            pyxel.text(8, 8, " ".join(effects), self._theme.accent)

    def draw(self) -> None:
        pyxel.cls(self._theme.bg)

        shake_x, shake_y = self._shake.offset(self._rng)
        cam_x = self._camera_x + shake_x
        cam_y = self._camera_y + shake_y

        water_screen_y = int(self._water_y - cam_y)
        if water_screen_y < HEIGHT:
            y = max(0, water_screen_y)
            pyxel.rect(0, y, WIDTH, HEIGHT - y, 12)

        for p in self._platforms:
            p.draw(cam_x, cam_y, self._theme.fg)

        for item in self._items:
            item.draw(cam_x, cam_y, self._theme.accent)

        for e in self._enemies:
            e.draw(cam_x, cam_y, self._theme.fg, self._theme.danger)

        self._particles.draw(cam_x, cam_y)
        self._player.draw(cam_x, cam_y, self._theme.accent, self._theme.shape_style)
        self._player.draw_face(cam_x, cam_y, self._character.eye_style, self._character.mouth_style, self._character.hat_style)

        if self._player.grounded and self._player.charge > 0:
            pr = self._player.rect()
            x = int(pr.x - cam_x)
            y = int(pr.y - cam_y)
            bar_w = 46
            bar_h = 5
            bx = x + pr.w // 2 - bar_w // 2
            by = y - 10
            pyxel.rect(bx - 1, by - 1, bar_w + 2, bar_h + 2, 0)
            pyxel.rect(bx, by, bar_w, bar_h, 5)
            pyxel.rect(bx, by, int(bar_w * self._player.charge), bar_h, self._theme.accent)

        self._draw_ui()

        prompt = self._theme.prompt
        if prompt:
            self._utext.blit(8, HEIGHT - 16, prompt[:60], 6)
