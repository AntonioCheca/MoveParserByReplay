from typing import List, Optional

from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction


class InputDisplayRow:
    direction: Optional[Direction]
    buttons: List[Button]
    pressed_frames: int

    def __init__(self, direction: Optional[Direction], buttons: List[Button], pressed_frames: int):
        self.direction = direction
        self.buttons = buttons
        self.pressed_frames = pressed_frames

    def get_direction(self) -> Optional[Direction]:
        return self.direction

    def get_buttons(self) -> List[Button]:
        return self.buttons

    def get_frame_number(self) -> int:
        return self.pressed_frames
