from typing import List, Optional, Self

from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons


class InputDisplayRow:
    direction: Optional[Direction]
    buttons: Optional[ListOfButtons]
    pressed_frames: Optional[int]

    def __init__(self, direction: Optional[Direction], buttons: Optional[ListOfButtons], pressed_frames: Optional[int]):
        self.direction = direction
        self.buttons = buttons
        self.pressed_frames = pressed_frames

    def get_direction(self) -> Optional[Direction]:
        return self.direction

    def get_buttons(self) -> Optional[ListOfButtons]:
        return self.buttons

    def get_frame_number(self) -> Optional[int]:
        return self.pressed_frames

    def __eq__(self, other: Self) -> bool:
        if other is None:
            return False
        return self.direction == other.direction and self.buttons == other.buttons and self.pressed_frames == other.pressed_frames

    def __hash__(self):
        return hash((self.direction, self.buttons, self.pressed_frames))
