from typing import List, Tuple

from move_parser_by_replay.base.templates.Button import Button


class ListOfButtons:
    buttons: Tuple[Button]

    def __init__(self, buttons: List[Button]):
        self.buttons = tuple(buttons)  # Convert list to tuple to make it immutable and hashable

    def __eq__(self, other):
        if not isinstance(other, ListOfButtons):
            return False
        return self.buttons == other.buttons

    def __hash__(self):
        return hash(self.buttons)  # Hash the tuple

    def __repr__(self):
        return f"ListOfButtons({self.buttons})"
