from __future__ import annotations

import os
from dataclasses import dataclass

from game.constants import HEIGHT, WATER_BASE_SPEED, WATER_SPEED_PER_FLOOR, WATER_START_OFFSET


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


@dataclass(frozen=True)
class GameConfig:
    scroll_start_player_screen_y: float
    fall_below_screen_px: float

    water_start_offset: float
    water_base_speed: float
    water_speed_per_floor: float

    zone_floor_step: int
    zone_popup_seconds: float

    ui_font_px: int
    ui_font_px_big: int
    title_font_px_big: int
    game_over_font_px_big: int

    @classmethod
    def load(cls) -> "GameConfig":
        default_scroll_y = HEIGHT * 0.60
        default_fall_below = HEIGHT * 0.80

        return cls(
            scroll_start_player_screen_y=float(
                _env_int("GAME_SCROLL_START_PLAYER_SCREEN_Y", int(default_scroll_y))
            ),
            fall_below_screen_px=float(_env_int("GAME_FALL_BELOW_SCREEN_PX", int(default_fall_below))),
            water_start_offset=float(_env_int("GAME_WATER_START_OFFSET", int(WATER_START_OFFSET))),
            water_base_speed=_env_float("GAME_WATER_BASE_SPEED", float(WATER_BASE_SPEED)),
            water_speed_per_floor=_env_float("GAME_WATER_SPEED_PER_FLOOR", float(WATER_SPEED_PER_FLOOR)),
            zone_floor_step=max(1, _env_int("GAME_ZONE_FLOOR_STEP", 10)),
            zone_popup_seconds=max(0.05, _env_float("GAME_ZONE_POPUP_SECONDS", 0.55)),
            # Keep general UI font sizes fixed to avoid too many tuning knobs.
            ui_font_px=18,
            ui_font_px_big=30,
            # Only title/game-over font sizes are user-tunable via .env.
            title_font_px_big=max(10, _env_int("GAME_TITLE_FONT_PX_BIG", 30)),
            game_over_font_px_big=max(10, _env_int("GAME_GAME_OVER_FONT_PX_BIG", 30)),
        )
