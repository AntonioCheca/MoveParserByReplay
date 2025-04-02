from typing import List, Tuple

from move_parser_by_replay.base.templates.Button import Button


class ListOfButtons:
    buttons: Tuple[Button]

    def __init__(self, buttons: List[Button]):
        self.buttons = tuple(set(buttons))  # Convert list to tuple to make it immutable and hashable

    def __eq__(self, other):
        if not isinstance(other, ListOfButtons):
            return False
        return self.get_unique_identifier() == other.get_unique_identifier()

    def __hash__(self):
        return hash(self.get_unique_identifier())

    def __repr__(self):
        unique_identifier = self.get_unique_identifier()
        return f"ListOfButtons({unique_identifier})"

    def append(self, button: Button) -> None:
        intermediate_list = list(self.buttons)
        intermediate_list.append(button)

        self.buttons = tuple(intermediate_list)

    def get_unique_identifier(self) -> str:
        list_of_button_names = [str(button) for button in self.buttons]
        unique_identifier = ', '.join(sorted(list_of_button_names))
        return unique_identifier
