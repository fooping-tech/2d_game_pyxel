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

    # Keyboard
    left_k = pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)
    right_k = pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D)
    jump_k = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)

    # Gamepad (Player 1)
    deadzone = 0.25
    axis_x = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
    left_g = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) or (axis_x < -deadzone)
    right_g = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) or (axis_x > deadzone)
    jump_g = pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)

    state.left = bool(left_k or left_g)
    state.right = bool(right_k or right_g)
    state.jump_down = bool(jump_k or jump_g)

    if prev is None:
        prev = InputState()
    state.jump_pressed = (not prev.jump_down) and state.jump_down
    state.jump_released = prev.jump_down and (not state.jump_down)

    state.confirm = (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_KP_ENTER)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
    )
    state.back = pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK)
    return state
