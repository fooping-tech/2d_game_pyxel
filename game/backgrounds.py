from __future__ import annotations

from dataclasses import dataclass

import pyxel


@dataclass(frozen=True)
class Zone:
    index: int
    name_jp: str
    bg: int
    dot: int
    accent: int


ZONES: list[Zone] = [
    Zone(0, "砂浜", bg=15, dot=10, accent=4),
    Zone(1, "道路", bg=6, dot=5, accent=0),
    Zone(2, "村", bg=11, dot=3, accent=4),
    Zone(3, "町", bg=13, dot=6, accent=1),
    Zone(4, "山", bg=3, dot=11, accent=0),
    Zone(5, "富士山", bg=12, dot=6, accent=7),
    Zone(6, "空", bg=12, dot=7, accent=6),
    Zone(7, "宇宙", bg=1, dot=13, accent=7),
    Zone(8, "月", bg=5, dot=6, accent=7),
    Zone(9, "火星", bg=2, dot=4, accent=8),
    Zone(10, "天国", bg=7, dot=15, accent=14),
]


def zone_for_floor(floor: int, *, step: int) -> Zone:
    if step <= 0:
        step = 10
    idx = max(0, floor // step)
    return ZONES[min(idx, len(ZONES) - 1)]

def _floor_for_world_y(*, start_y: float, world_y: float, floor_height_px: int) -> int:
    if floor_height_px <= 0:
        floor_height_px = 120
    return max(0, int((start_y - world_y) / floor_height_px))


def draw_scrolling_background(
    *,
    start_y: float,
    cam_y: float,
    floor_height_px: int,
    zone_step: int,
    tick: int,
) -> None:
    """
    Draw a world-anchored background that scrolls with the camera.
    Zone transitions (by floor) appear as boundaries moving through the screen.
    """
    int_cam_y = int(cam_y)

    # Draw in coarse horizontal stripes to keep it cheap.
    stripe_h = 6
    for sy in range(0, pyxel.height, stripe_h):
        world_y = int_cam_y + sy + stripe_h // 2
        floor = _floor_for_world_y(start_y=start_y, world_y=float(world_y), floor_height_px=floor_height_px)
        zone = zone_for_floor(floor, step=zone_step)
        pyxel.rect(0, sy, pyxel.width, stripe_h, zone.bg)

    # Light dot pattern, stable in world coordinates.
    dot_step = 8
    for sy in range(0, pyxel.height, dot_step):
        world_y = int_cam_y + sy
        floor = _floor_for_world_y(start_y=start_y, world_y=float(world_y), floor_height_px=floor_height_px)
        zone = zone_for_floor(floor, step=zone_step)
        x0 = (world_y // dot_step) % dot_step
        for sx in range(x0, pyxel.width, dot_step):
            pyxel.pset(sx, sy, zone.dot)

    # Zone-specific motifs, repeated in world space (so they scroll).
    zone_h = max(1, floor_height_px * max(1, zone_step))
    top_world = int_cam_y
    bottom_world = int_cam_y + pyxel.height
    first_band = (top_world // zone_h) - 1
    last_band = (bottom_world // zone_h) + 1

    for band in range(first_band, last_band + 1):
        band_top = band * zone_h
        band_bottom = band_top + zone_h
        band_mid = (band_top + band_bottom) // 2
        floor_mid = _floor_for_world_y(start_y=start_y, world_y=float(band_mid), floor_height_px=floor_height_px)
        zone = zone_for_floor(floor_mid, step=zone_step)

        # Only draw if the band overlaps the screen.
        if band_bottom < top_world or band_top > bottom_world:
            continue

        _draw_zone_motif(zone, int_cam_y=int_cam_y, band_top=band_top, band_bottom=band_bottom, tick=tick)

    _draw_pale_overlay(tick=tick)


def _draw_zone_motif(zone: Zone, *, int_cam_y: int, band_top: int, band_bottom: int, tick: int) -> None:
    # Convert a world y position to screen y.
    def sy(world_y: int) -> int:
        return world_y - int_cam_y

    w = pyxel.width
    h = pyxel.height

    if zone.index == 0:
        # Beach: gentle wave lines.
        for wy in range(band_top, band_bottom, 48):
            y = sy(wy + 22)
            if 0 <= y < h:
                for x in range(0, w, 6):
                    dy = 1 if ((x + (wy // 6)) % 12) == 0 else 0
                    pyxel.pset(x, y + dy, zone.accent)
    elif zone.index == 1:
        # Road: vertical road with dashed center line scrolling in world space.
        road_w = 320
        x0 = w // 2 - road_w // 2
        pyxel.rect(x0, 0, road_w, h, zone.dot)
        pyxel.rectb(x0, 0, road_w, h, 0)
        dash = 18
        x = w // 2
        offset = ((int_cam_y + tick * 2) // 2) % (dash * 2)
        for y in range(-dash * 2, h + dash * 2, dash * 2):
            pyxel.rect(x - 2, y + offset, 4, dash, zone.accent)
    elif zone.index == 2:
        # Village: small houses every ~140px.
        period = 140
        for wy in range((band_top // period - 1) * period, band_bottom + period, period):
            y = sy(wy + 80)
            if y < -40 or y > h + 40:
                continue
            base = (wy // period) * 97
            for x in (80 + (base % 120), 260 + (base % 140), 640 + (base % 160)):
                pyxel.rect(x, y, 46, 28, zone.accent)
                pyxel.tri(x - 2, y, x + 23, y - 20, x + 48, y, 4)
                pyxel.rect(x + 10, y + 10, 10, 18, 0)
    elif zone.index == 3:
        # Town: buildings rows.
        period = 120
        for wy in range((band_top // period - 1) * period, band_bottom + period, period):
            y0 = sy(wy + 90)
            if y0 < -120 or y0 > h + 60:
                continue
            for i, x in enumerate(range(40, w - 40, 90)):
                bh = 50 + ((i + (wy // period)) % 5) * 18
                pyxel.rect(x, y0 - bh, 60, bh, zone.dot)
                pyxel.rectb(x, y0 - bh, 60, bh, 0)
                for wy2 in range(y0 - bh + 8, y0 - 6, 12):
                    pyxel.rect(x + 8, wy2, 8, 5, zone.accent)
    elif zone.index == 4:
        # Mountains: triangle silhouettes.
        y_base = sy(band_top + 180)
        for x in range(-80, w + 80, 140):
            pyxel.tri(x, y_base, x + 70, y_base - 120, x + 140, y_base, zone.accent)
            pyxel.tri(x + 10, y_base, x + 70, y_base - 90, x + 130, y_base, zone.dot)
    elif zone.index == 5:
        # Fuji: big mountain occasionally.
        period = 360
        for wy in range((band_top // period - 1) * period, band_bottom + period, period):
            y = sy(wy + 260)
            if y < -320 or y > h + 320:
                continue
            cx = w // 2
            pyxel.tri(cx - 240, y, cx, y - 280, cx + 240, y, zone.dot)
            pyxel.tri(cx - 140, y, cx, y - 220, cx + 140, y, zone.accent)
            pyxel.tri(cx - 70, y - 220, cx, y - 280, cx + 70, y - 220, 7)
    elif zone.index == 6:
        # Sky: drifting clouds.
        period = 160
        for wy in range((band_top // period - 1) * period, band_bottom + period, period):
            y = sy(wy + (tick // 10) % period)
            if y < -40 or y > h + 40:
                continue
            base = (wy // period) * 53
            _cloud(160 + (base % 120), y, col=7)
            _cloud(520 + (base % 160), y + 40, col=7)
            _cloud(820 + (base % 200), y + 10, col=7)
    elif zone.index == 7:
        # Space: stars (already dotted); add occasional planet.
        y = sy((band_top + band_bottom) // 2)
        if 0 <= y < h:
            pyxel.circ(w - 140, y, 34, zone.accent)
            pyxel.circb(w - 140, y, 34, 7)
    elif zone.index == 8:
        # Moon: craters repeating.
        period = 220
        for wy in range((band_top // period - 1) * period, band_bottom + period, period):
            y = sy(wy + 120)
            if y < -60 or y > h + 60:
                continue
            base = (wy // period) * 31
            for x, r in [(180 + base % 140, 18), (480 + base % 200, 12), (760 + base % 160, 22)]:
                pyxel.circ(x, y, r, zone.dot)
                pyxel.circb(x, y, r, zone.accent)
    elif zone.index == 9:
        # Mars: dusty ground band.
        for wy in range(band_top, band_bottom, 180):
            y = sy(wy + 130)
            if y < -200 or y > h + 200:
                continue
            pyxel.rect(0, y, w, 90, zone.dot)
            for x in range(40, w - 40, 110):
                pyxel.circ(x, y + 40, 9, zone.accent)
    else:
        # Heaven: rays.
        shift = (int_cam_y // 6 + tick // 3) % 120
        for i in range(10):
            x = (i * 120 + shift) % w
            pyxel.rect(x, 0, 18, h, zone.dot)
        pyxel.circb(w // 2, 120, 46, zone.accent)


def _draw_pale_overlay(*, tick: int) -> None:
    """
    Lighten the whole background without alpha by drawing sparse white dots.
    Keep this after motifs so the palette looks washed/pale.
    """
    step = 2
    phase = (tick // 10) % 2
    for y in range(0, pyxel.height, step):
        x0 = (y // step + phase) % 2
        for x in range(x0, pyxel.width, 4):
            pyxel.pset(x, y, 7)


def draw_zone_background(zone: Zone, *, tick: int) -> None:
    pyxel.cls(zone.bg)

    # Light dot pattern
    spacing = 4
    jitter = (tick // 6) % spacing
    for y in range(0, pyxel.height, spacing):
        for x in range((y + jitter) % spacing, pyxel.width, spacing):
            pyxel.pset(x, y, zone.dot)

    if zone.index == 0:
        _draw_beach()
    elif zone.index == 1:
        _draw_road(tick=tick)
    elif zone.index == 2:
        _draw_village()
    elif zone.index == 3:
        _draw_town()
    elif zone.index == 4:
        _draw_mountains()
    elif zone.index == 5:
        _draw_fuji()
    elif zone.index == 6:
        _draw_sky(tick=tick)
    elif zone.index == 7:
        _draw_space(tick=tick)
    elif zone.index == 8:
        _draw_moon()
    elif zone.index == 9:
        _draw_mars()
    else:
        _draw_heaven(tick=tick)


def _draw_beach() -> None:
    # Horizon band
    pyxel.rect(0, pyxel.height - 120, pyxel.width, 120, 15)
    pyxel.rect(0, pyxel.height - 120, pyxel.width, 2, 10)


def _draw_road(*, tick: int) -> None:
    w = pyxel.width
    h = pyxel.height
    # Road body
    pyxel.rect(w // 2 - 160, 0, 320, h, 5)
    pyxel.rectb(w // 2 - 160, 0, 320, h, 0)
    # Center dashed line
    dash = 18
    offset = (tick // 2) % (dash * 2)
    x = w // 2
    for y in range(-dash * 2, h + dash * 2, dash * 2):
        pyxel.rect(x - 2, y + offset, 4, dash, 10)


def _draw_village() -> None:
    # Grass band
    pyxel.rect(0, pyxel.height - 150, pyxel.width, 150, 11)
    # Small houses
    for i, x in enumerate(range(80, pyxel.width - 80, 180)):
        y = pyxel.height - 120 - (i % 2) * 18
        pyxel.rect(x, y, 46, 28, 7)
        pyxel.tri(x - 2, y, x + 23, y - 20, x + 48, y, 4)
        pyxel.rect(x + 10, y + 10, 10, 18, 0)


def _draw_town() -> None:
    # Buildings
    base_y = pyxel.height - 160
    for i, x in enumerate(range(40, pyxel.width - 40, 80)):
        h = 40 + (i % 5) * 14
        pyxel.rect(x, base_y - h, 50, h, 6)
        pyxel.rectb(x, base_y - h, 50, h, 0)
        for wy in range(base_y - h + 6, base_y - 6, 10):
            pyxel.rect(x + 6, wy, 6, 4, 10)


def _draw_mountains() -> None:
    y = pyxel.height - 120
    for x in range(-80, pyxel.width + 80, 120):
        pyxel.tri(x, y, x + 60, y - 90, x + 120, y, 11)
        pyxel.tri(x + 10, y, x + 60, y - 70, x + 110, y, 3)


def _draw_fuji() -> None:
    w = pyxel.width
    h = pyxel.height
    base_y = h - 110
    cx = w // 2
    pyxel.tri(cx - 220, base_y, cx, base_y - 260, cx + 220, base_y, 13)
    pyxel.tri(cx - 120, base_y, cx, base_y - 200, cx + 120, base_y, 12)
    # Snow cap
    pyxel.tri(cx - 60, base_y - 200, cx, base_y - 260, cx + 60, base_y - 200, 7)


def _draw_sky(*, tick: int) -> None:
    # Clouds
    y = 70 + (tick // 10) % 30
    for x in (120, 380, 680):
        _cloud(x, y, col=7)
        y += 50


def _draw_space(*, tick: int) -> None:
    # Stars
    for i in range(180):
        x = (i * 97 + tick * 3) % pyxel.width
        y = (i * 53 + tick * 2) % pyxel.height
        pyxel.pset(x, y, 7 if (i % 3) == 0 else 13)


def _draw_moon() -> None:
    # Craters
    for x, y, r in [(160, 140, 18), (420, 220, 12), (760, 120, 22), (640, 320, 16)]:
        pyxel.circ(x, y, r, 6)
        pyxel.circb(x, y, r, 5)


def _draw_mars() -> None:
    # Dust / rocks
    pyxel.rect(0, pyxel.height - 140, pyxel.width, 140, 4)
    for x in range(40, pyxel.width - 40, 90):
        pyxel.circ(x, pyxel.height - 90, 8, 2)
        pyxel.circ(x + 30, pyxel.height - 70, 6, 2)


def _draw_heaven(*, tick: int) -> None:
    # Soft beams
    for i in range(10):
        x = (i * 120 + (tick // 2)) % pyxel.width
        pyxel.rect(x, 0, 18, pyxel.height, 15)
    # Halo
    pyxel.circb(pyxel.width // 2, 120, 46, 10)


def _cloud(x: int, y: int, *, col: int) -> None:
    pyxel.circ(x, y, 18, col)
    pyxel.circ(x + 18, y + 6, 14, col)
    pyxel.circ(x - 18, y + 8, 12, col)
    pyxel.rect(x - 28, y + 6, 56, 18, col)
