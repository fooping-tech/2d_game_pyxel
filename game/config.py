from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from game.constants import HEIGHT, WATER_BASE_SPEED, WATER_SPEED_PER_FLOOR, WATER_START_OFFSET

try:
    import tomllib  # py3.11+
except Exception:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found]


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


def _find_config_toml() -> Path | None:
    # Priority: explicit path, then repo/app root relative to this file, then CWD.
    env = os.environ.get("GAME_CONFIG_PATH", "").strip()
    if env:
        p = Path(env)
        if p.exists():
            return p

    here_root = Path(__file__).resolve().parents[1]  # .../app or repo root
    p1 = here_root / "config.toml"
    if p1.exists():
        return p1

    p2 = Path.cwd() / "config.toml"
    if p2.exists():
        return p2

    return None


def _read_toml_config() -> dict:
    p = _find_config_toml()
    if p is None:
        return {}
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


def _get_path(d: dict, path: str):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _toml_int(d: dict, path: str, default: int) -> int:
    v = _get_path(d, path)
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def _toml_float(d: dict, path: str, default: float) -> float:
    v = _get_path(d, path)
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def _toml_str(d: dict, path: str, default: str) -> str:
    v = _get_path(d, path)
    if v is None:
        return default
    return str(v)


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
    zone_text_font_px: int
    zone_text_font_px_big: int

    sfx_volume: float
    bgm_volume: float
    lang: str

    @classmethod
    def load(cls) -> "GameConfig":
        default_scroll_y = HEIGHT * 0.60
        default_fall_below = HEIGHT * 0.80
        cfg = _read_toml_config()
        lang = _toml_str(cfg, "game.lang", "auto").strip().lower()
        is_web = sys.platform == "emscripten"

        # Defaults from TOML (shared across desktop/web).
        base = cls(
            scroll_start_player_screen_y=float(_toml_int(cfg, "game.scroll_start_player_screen_y", int(default_scroll_y))),
            fall_below_screen_px=float(_toml_int(cfg, "game.fall_below_screen_px", int(default_fall_below))),
            water_start_offset=float(_toml_int(cfg, "game.water_start_offset", int(WATER_START_OFFSET))),
            water_base_speed=_toml_float(cfg, "game.water_base_speed", float(WATER_BASE_SPEED)),
            water_speed_per_floor=_toml_float(cfg, "game.water_speed_per_floor", float(WATER_SPEED_PER_FLOOR)),
            zone_floor_step=max(1, _toml_int(cfg, "game.zone_floor_step", 10)),
            zone_popup_seconds=max(0.05, _toml_float(cfg, "game.zone_popup_seconds", 0.55)),
            ui_font_px=max(8, _toml_int(cfg, "game.ui_font_px", 18)),
            ui_font_px_big=max(10, _toml_int(cfg, "game.ui_font_px_big", 30)),
            title_font_px_big=max(10, _toml_int(cfg, "game.title_font_px_big", 30)),
            game_over_font_px_big=max(10, _toml_int(cfg, "game.game_over_font_px_big", 30)),
            zone_text_font_px=max(8, _toml_int(cfg, "game.zone_text_font_px", 22)),
            zone_text_font_px_big=max(10, _toml_int(cfg, "game.zone_text_font_px_big", 36)),
            sfx_volume=max(0.0, min(1.0, _toml_float(cfg, "game.sfx_volume", 0.9))),
            bgm_volume=max(0.0, min(1.0, _toml_float(cfg, "game.bgm_volume", 0.55))),
            lang=lang,
        )

        # Local override only (web can't use env/.env reliably).
        if is_web:
            return base

        return cls(
            scroll_start_player_screen_y=float(_env_int("GAME_SCROLL_START_PLAYER_SCREEN_Y", int(base.scroll_start_player_screen_y))),
            fall_below_screen_px=float(_env_int("GAME_FALL_BELOW_SCREEN_PX", int(base.fall_below_screen_px))),
            water_start_offset=float(_env_int("GAME_WATER_START_OFFSET", int(base.water_start_offset))),
            water_base_speed=_env_float("GAME_WATER_BASE_SPEED", float(base.water_base_speed)),
            water_speed_per_floor=_env_float("GAME_WATER_SPEED_PER_FLOOR", float(base.water_speed_per_floor)),
            zone_floor_step=max(1, _env_int("GAME_ZONE_FLOOR_STEP", int(base.zone_floor_step))),
            zone_popup_seconds=max(0.05, _env_float("GAME_ZONE_POPUP_SECONDS", float(base.zone_popup_seconds))),
            ui_font_px=max(8, _env_int("GAME_UI_FONT_PX", int(base.ui_font_px))),
            ui_font_px_big=max(10, _env_int("GAME_UI_FONT_PX_BIG", int(base.ui_font_px_big))),
            title_font_px_big=max(10, _env_int("GAME_TITLE_FONT_PX_BIG", int(base.title_font_px_big))),
            game_over_font_px_big=max(10, _env_int("GAME_GAME_OVER_FONT_PX_BIG", int(base.game_over_font_px_big))),
            zone_text_font_px=max(8, _env_int("GAME_ZONE_TEXT_FONT_PX", int(base.zone_text_font_px))),
            zone_text_font_px_big=max(10, _env_int("GAME_ZONE_TEXT_FONT_PX_BIG", int(base.zone_text_font_px_big))),
            sfx_volume=max(0.0, min(1.0, _env_float("GAME_SFX_VOLUME", float(base.sfx_volume)))),
            bgm_volume=max(0.0, min(1.0, _env_float("GAME_BGM_VOLUME", float(base.bgm_volume)))),
            lang=os.environ.get("GAME_LANG", base.lang),
        )
