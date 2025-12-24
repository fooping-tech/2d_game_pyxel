from __future__ import annotations

from dataclasses import dataclass

import pyxel


@dataclass
class InputState:
    left: bool = False
    right: bool = False
    jump_down: bool = False
    jump_pressed: bool = False
    jump_released: bool = False
    confirm: bool = False
    back: bool = False


def read_input(prev: InputState | None) -> InputState:
    state = InputState()

    state.left = pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)
    state.right = pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D)
    state.jump_down = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)

    if prev is None:
        prev = InputState()
    state.jump_pressed = (not prev.jump_down) and state.jump_down
    state.jump_released = prev.jump_down and (not state.jump_down)

    state.confirm = pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER)
    state.back = pyxel.btnp(pyxel.KEY_ESCAPE)
    return state

