import os
from typing import Dict, List

from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.input_display.InputDisplayObservationManager import InputDisplayObservationManager
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow


class InputDisplayObserver:
    TEMPLATES_FOR_INPUTS = './data/input_display/'
    TEMPLATES_FOR_NUMBERS = './data/numbers/'

    directions: Dict[str, Direction]
    buttons: Dict[str, Button]
    numbers: Dict[str, Number]
    exact_input_rows: List[InputDisplayRow]
    input_display_manager: InputDisplayObservationManager

    def __init__(self, video: Video):
        self.initialise_buttons()
        self.initialise_directions()
        self.initialise_numbers()
        self.exact_input_rows = []
        self.input_display_manager = InputDisplayObservationManager(self.get_numbers(), self.get_buttons(),
                                                                    self.get_directions(), video)

    def initialise_directions(self) -> None:
        self.directions = {}
        self.load_templates_from_folder("Direction")

    def initialise_buttons(self) -> None:
        self.buttons = {}
        self.load_templates_from_folder("Button")

    def initialise_numbers(self) -> None:
        self.numbers = {}
        self.load_templates_from_folder("Number", self.TEMPLATES_FOR_NUMBERS)

    def load_templates_from_folder(self, item_type: str, folder: str = TEMPLATES_FOR_INPUTS) -> None:
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Templates directory not found: {folder}")

        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            base_name = os.path.splitext(file_name)[0]

            if os.path.isfile(file_path):
                if item_type == "Direction" and "Direction" in file_name:
                    self.directions[base_name] = Direction(file_path)
                elif item_type == "Button" and "Direction" not in file_name:
                    self.buttons[base_name] = Button(file_path)
                elif item_type == "Number":
                    self.numbers[base_name] = Number(file_path)

    def get_buttons(self) -> Dict[str, Button]:
        return self.buttons

    def get_directions(self) -> Dict[str, Direction]:
        return self.directions

    def get_numbers(self) -> Dict[str, Number]:
        return self.numbers

    def get_manager(self) -> InputDisplayObservationManager:
        return self.input_display_manager

    def get_exact_input_rows(self) -> List[InputDisplayRow]:
        return self.exact_input_rows
