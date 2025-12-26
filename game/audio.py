from __future__ import annotations

import os
from dataclasses import dataclass

import pyxel


@dataclass
class AudioManager:
    enabled: bool = True
    master_volume: float = 0.7
    sfx_volume: float = 0.9

    def __post_init__(self) -> None:
        self._name_to_sound: dict[str, int] = {}
        self._name_to_channel: dict[str, int] = {}
        self._cooldown_frames: dict[str, int] = {}
        self._last_play_frame: dict[str, int] = {}
        self.debug: str = "pyxel"

    @classmethod
    def create(cls) -> "AudioManager":
        mute = os.environ.get("GAME_MUTE", "").strip() not in ("", "0", "false", "False")
        mgr = cls(enabled=not mute)
        mgr._load_defaults()
        return mgr

    def _add(self, name: str, sound_id: int, *, channel: int, cooldown_frames: int = 0) -> None:
        self._name_to_sound[name] = sound_id
        self._name_to_channel[name] = channel
        self._cooldown_frames[name] = cooldown_frames

    def _load_defaults(self) -> None:
        # Sound IDs 0..7 reserved
        pyxel.sounds[0].set("c3g3c4", "t", "7", "n", 10)  # ui_confirm
        pyxel.sounds[1].set("c2g2c3", "t", "6", "n", 12)  # jump
        pyxel.sounds[2].set("c1", "n", "5", "n", 8)  # land
        pyxel.sounds[3].set("g3c4e4", "t", "6", "n", 12)  # pickup
        pyxel.sounds[4].set("c1c1", "n", "7", "n", 16)  # stomp
        pyxel.sounds[5].set("c1d1", "n", "7", "n", 18)  # hit
        pyxel.sounds[6].set("c2b1a1", "t", "5", "n", 24)  # game_over
        pyxel.sounds[7].set("g3", "t", "4", "n", 8)  # water_warn
        pyxel.sounds[8].set("c3d3e3f3g3a3b3c4", "t", "2", "n", 30)  # charge loop-ish
        pyxel.sounds[9].set("c4e4g4c4", "t", "6", "n", 14)  # zone_change

        self._add("ui_confirm", 0, channel=0, cooldown_frames=4)
        self._add("jump", 1, channel=0, cooldown_frames=4)
        self._add("land", 2, channel=0, cooldown_frames=3)
        self._add("pickup", 3, channel=0, cooldown_frames=3)
        self._add("stomp", 4, channel=0, cooldown_frames=4)
        self._add("hit", 5, channel=0, cooldown_frames=8)
        self._add("game_over", 6, channel=0, cooldown_frames=30)
        self._add("water_warn", 7, channel=0, cooldown_frames=55)
        self._add("charge", 8, channel=1, cooldown_frames=0)
        self._add("zone_change", 9, channel=0, cooldown_frames=18)

    def play(self, name: str, *, volume: float = 1.0) -> None:
        if not self.enabled:
            return
        sound_id = self._name_to_sound.get(name)
        if sound_id is None:
            return
        channel = self._name_to_channel.get(name, 0)
        now = pyxel.frame_count
        last = self._last_play_frame.get(name, -10**9)
        cd = self._cooldown_frames.get(name, 0)
        if now - last < cd:
            return
        self._last_play_frame[name] = now
        _ = volume * self.master_volume * self.sfx_volume
        pyxel.play(channel, sound_id, loop=False)

    def play_loop(self, name: str, *, volume: float = 1.0) -> None:
        if not self.enabled:
            return
        sound_id = self._name_to_sound.get(name)
        if sound_id is None:
            return
        channel = self._name_to_channel.get(name, 1)
        if pyxel.play_pos(channel) is not None:
            return
        _ = volume * self.master_volume * self.sfx_volume
        pyxel.play(channel, sound_id, loop=True)

    def stop_loop(self, name: str) -> None:
        channel = self._name_to_channel.get(name)
        if channel is None:
            return
        pyxel.stop(channel)
