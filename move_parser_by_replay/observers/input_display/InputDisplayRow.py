from typing import List, Optional, Self

from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons


class InputDisplayRow:
    UNKNOWN_TAG = 'UNKNOWN'

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

    def __repr__(self) -> str:
        return "Direction:{}, Buttons:{}, Frames: {}".format(self.get_string_for_direction(),
                                                             self.get_string_for_buttons(),
                                                             self.get_string_for_frames())

    def get_string_for_frames(self) -> str:
        if self.pressed_frames is None:
            return self.UNKNOWN_TAG
        return str(self.pressed_frames)

    def get_string_for_direction(self) -> str:
        if self.direction is None:
            return self.UNKNOWN_TAG
        return str(self.direction)

    def get_string_for_buttons(self) -> str:
        if self.buttons is None:
            return self.UNKNOWN_TAG
        return str(self.buttons)

    def get_differences_with_other_input_display_row(self, other: Self) -> List[str]:
        differences = []

        if self.direction != other.direction:
            differences.append('Direction, {} vs {}'.format(str(self.direction), str(other.direction)))
        if self.pressed_frames != other.pressed_frames:
            differences.append('Frames pressed, {} vs {}'.format(str(self.pressed_frames), str(other.pressed_frames)))
        if self.buttons != other.buttons:
            differences.append('Buttons, {} vs {}'.format(str(self.buttons), str(other.buttons)))

        return differences

    @classmethod
    def get_empty_row(cls) -> Self:
        return InputDisplayRow(None, ListOfButtons([]), None)
