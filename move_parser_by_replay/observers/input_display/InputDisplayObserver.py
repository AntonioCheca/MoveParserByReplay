from typing import Dict, List

from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.AbstractTemplateObserver import AbstractTemplateObserver
from move_parser_by_replay.observers.input_display.InputDisplayObservationManager import InputDisplayObservationManager
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow


class InputDisplayTemplateObserver(AbstractTemplateObserver):
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
        self.directions = self.load_templates_from_folder(self.TEMPLATES_FOR_INPUTS, Direction)

    def initialise_buttons(self) -> None:
        self.buttons = self.load_templates_from_folder(self.TEMPLATES_FOR_INPUTS, Button)

    def initialise_numbers(self) -> None:
        self.numbers = self.load_templates_from_folder(self.TEMPLATES_FOR_NUMBERS, Number)

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
