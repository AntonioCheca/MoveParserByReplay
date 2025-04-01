from typing import Dict, List, cast, Self

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.base.templates.TemplateImage import TemplateImage
from move_parser_by_replay.observers.input_display.InputDisplayObservationRow import InputDisplayObservationRow
from move_parser_by_replay.util.RecognisedTemplateInPosition import RecognisedTemplateInPosition
from move_parser_by_replay.util.number_recognisers.MatchTemplateNumberRecogniser import MatchTemplateNumberRecogniser
from move_parser_by_replay.util.number_recognisers.RecognisedNumberInPosition import RecognisedNumberInPosition


class InputDisplayObservation:
    MAX_ROWS_TO_OBSERVE = 19
    MINIMUM_ROWS_FOR_OVERLAPS = 4
    SUCCESS_THRESHOLD_FOR_COMPARING_ROWS = 0.5

    observation_rows_by_player: Dict[Player, Dict[int, InputDisplayObservationRow]]
    raw_frame_number: int

    def __init__(self, raw_frame_number: int,
                 observation_rows_by_player: Dict[Player, Dict[int, InputDisplayObservationRow]] = None):
        self.raw_frame_number = raw_frame_number
        if observation_rows_by_player is not None:
            self.observation_rows_by_player = observation_rows_by_player
        else:
            self.initialise_observation_rows_by_player()

    def initialise_observation_rows_by_player(self) -> None:
        first_player_dict: Dict[int, InputDisplayObservationRow] = {}
        second_player_dict: Dict[int, InputDisplayObservationRow] = {}
        for row_number in range(1, self.MAX_ROWS_TO_OBSERVE + 1):
            first_player_dict[row_number] = InputDisplayObservationRow()
            second_player_dict[row_number] = InputDisplayObservationRow()

        self.observation_rows_by_player = {Player.FIRST_PLAYER: first_player_dict,
                                           Player.SECOND_PLAYER: second_player_dict}

    def get_observation_rows_by_player(self) -> Dict[Player, Dict[int, InputDisplayObservationRow]]:
        return self.observation_rows_by_player

    def get_observation_rows_by_list_of_ints_and_player(self, player: Player,
                                                        list_of_rows: List[int]) -> List[InputDisplayObservationRow]:
        list_observation_rows = []
        for row in list_of_rows:
            list_observation_rows.append(self.observation_rows_by_player[player][row])

        return list_observation_rows

    def add_observation_of_buttons(self, list_of_buttons_recognised: List[RecognisedTemplateInPosition],
                                   player: Player) -> None:
        buttons_by_row = self.get_templates_grouped_by_row(list_of_buttons_recognised)
        buttons_by_row = cast(Dict[int, List[Button]], buttons_by_row)

        for row_key in buttons_by_row:
            buttons = buttons_by_row[row_key]
            list_of_buttons = ListOfButtons(buttons)
            self.observation_rows_by_player[player][row_key].add_buttons_pressed_observation(list_of_buttons, 9)

    def add_observation_of_directions(self, list_of_directions_recognised: List[RecognisedTemplateInPosition],
                                      player: Player) -> None:
        for direction_recognised in list_of_directions_recognised:
            mapped_row = self.map_y_from_position_to_row_key(direction_recognised.get_position().get_y())

            direction = cast(Direction, direction_recognised.get_template())
            self.observation_rows_by_player[player][mapped_row].add_direction_pressed_observation(direction, 9)

    def add_observation_of_frames_pressed(self, list_of_pressed_frames_recognised: List[RecognisedNumberInPosition],
                                          player: Player) -> None:
        for number_recognised in list_of_pressed_frames_recognised:
            mapped_row = self.map_y_from_position_to_row_key(number_recognised.get_position().get_y())

            number = number_recognised.get_number()
            if 0 <= number <= 99:
                self.observation_rows_by_player[player][mapped_row].add_frames_pressed_observation(number, 1)

    def get_templates_grouped_by_row(self, list_of_buttons_recognised) -> Dict[int, List[TemplateImage]]:
        buttons_by_row: Dict[int, List[TemplateImage]] = {}
        for button_recognised in list_of_buttons_recognised:
            mapped_row = self.map_y_from_position_to_row_key(button_recognised.get_position().get_y())
            if mapped_row not in buttons_by_row:
                buttons_by_row[mapped_row] = []

            button = button_recognised.get_template()
            buttons_by_row[mapped_row].append(button)
        return buttons_by_row

    @classmethod
    def map_y_from_position_to_row_key(cls, y_from_position: int) -> int:
        bottom_y = MatchTemplateNumberRecogniser.BOTTOM_Y_FOR_SUBREGION
        top_y = MatchTemplateNumberRecogniser.HEIGHT_Y_FOR_SUBREGION + bottom_y
        total_size = top_y - bottom_y
        row_size = total_size / cls.MAX_ROWS_TO_OBSERVE

        relative_y = y_from_position
        guessed_row = int(relative_y / row_size)

        if guessed_row == cls.MAX_ROWS_TO_OBSERVE + 1:
            return cls.MAX_ROWS_TO_OBSERVE

        return guessed_row + 1

    def is_observation_inside_other_observation_slided_n_rows(self, other_observation: Self,
                                                              slided_rows_number: int,
                                                              player: Player) -> bool:
        overlapped_rows = self.MAX_ROWS_TO_OBSERVE - slided_rows_number - 1

        if overlapped_rows < self.MINIMUM_ROWS_FOR_OVERLAPS:
            return False

        success_count = 0
        for row_key in range(2, 2 + overlapped_rows):
            first_row = self.observation_rows_by_player[player][row_key]
            row_to_compare = other_observation.observation_rows_by_player[player][row_key + slided_rows_number]
            probability = first_row.get_probability_this_is_same_row_than(row_to_compare)
            if probability >= self.SUCCESS_THRESHOLD_FOR_COMPARING_ROWS:
                success_count += 1

        return success_count >= overlapped_rows // 2
