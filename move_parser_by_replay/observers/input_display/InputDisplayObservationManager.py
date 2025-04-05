from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.AbstractBinarySearchObserver import AbstractBinarySearchObserver
from move_parser_by_replay.observers.input_display.InputDisplayObservation import InputDisplayObservation
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.observers.input_display.MergerForInputDisplayObservations import \
    MergerForInputDisplayObservations
from move_parser_by_replay.util.button_recognisers.MatchTemplateButtonRecogniser import MatchTemplateButtonRecogniser
from move_parser_by_replay.util.direction_recognisers.MatchTemplateDirectionRecogniser import \
    MatchTemplateDirectionRecogniser
from move_parser_by_replay.util.number_recognisers.EasyOCRNumberRecogniser import EasyOCRNumberRecogniser
from move_parser_by_replay.util.number_recognisers.MatchTemplateNumberRecogniser import MatchTemplateNumberRecogniser
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface


class InputDisplayObservationManager(AbstractBinarySearchObserver):
    number_recognisers: List[NumberRecogniserInterface]
    button_recogniser: MatchTemplateButtonRecogniser
    direction_recogniser: MatchTemplateDirectionRecogniser

    observations: Dict[int, InputDisplayObservation]

    def __init__(self, numbers_template: Dict[str, Number], buttons_template: Dict[str, Button],
                 directions_template: Dict[str, Direction], video: Video):
        super().__init__(video)
        self.number_recognisers = []

        self.number_recognisers.append(EasyOCRNumberRecogniser())
        self.number_recognisers.append(MatchTemplateNumberRecogniser(numbers_template))
        self.button_recogniser = MatchTemplateButtonRecogniser(buttons_template)
        self.direction_recogniser = MatchTemplateDirectionRecogniser(directions_template)

        self.observations = {}

    def get_observations(self) -> Dict[int, InputDisplayObservation]:
        return self.observations

    def apply_specific_observations_in_frame(self, frame_number: int):
        frame = self.video.get_frame_from_position(frame_number)

        self.apply_observations_for_player(frame, Player.FIRST_PLAYER, frame_number)
        self.apply_observations_for_player(frame, Player.SECOND_PLAYER, frame_number)

    def get_saved_observation_in_frame(self, frame_number: int):
        return self.observations[frame_number]

    def get_merge_observation_in_two_frames(self, first_frame: int, second_frame: int) -> List:
        return MergerForInputDisplayObservations.merge_input_displays(
            self.observations[first_frame], first_frame, self.observations[second_frame], second_frame,
            Player.FIRST_PLAYER)

    def apply_observations_for_player(self, frame: Frame, player: Player, frame_number: int) -> None:
        subregion_for_buttons = MatchTemplateButtonRecogniser.get_subregion(frame, player)
        buttons_recognised = self.button_recogniser.search_templates_in_image(subregion_for_buttons)

        if frame_number not in self.observations:
            self.observations[frame_number] = InputDisplayObservation(frame_number)

        self.observations[frame_number].add_observation_of_buttons(buttons_recognised, player)

        subregion_for_directions = MatchTemplateDirectionRecogniser.get_subregion(frame, player)
        directions_recognised = self.direction_recogniser.search_templates_in_image(subregion_for_directions)
        self.observations[frame_number].add_observation_of_directions(directions_recognised, player)

        subregion_for_numbers = MatchTemplateNumberRecogniser.get_subregion(frame, player)
        for number_recogniser in self.number_recognisers:
            numbers_recognised = number_recogniser.get_numbers_in_region(subregion_for_numbers)
            self.observations[frame_number].add_observation_of_frames_pressed(numbers_recognised, player)

    def clean_final_list_if_needed(self) -> None:

        self.exact_final_list = [row for row in self.exact_final_list if row != InputDisplayRow.get_empty_row()]
