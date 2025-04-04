import bisect
from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.input_display.InputDisplayObservation import InputDisplayObservation
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.observers.input_display.MergerForInputDisplayObservations import \
    MergerForInputDisplayObservations
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper
from move_parser_by_replay.util.button_recognisers.MatchTemplateButtonRecogniser import MatchTemplateButtonRecogniser
from move_parser_by_replay.util.direction_recognisers.MatchTemplateDirectionRecogniser import \
    MatchTemplateDirectionRecogniser
from move_parser_by_replay.util.number_recognisers.EasyOCRNumberRecogniser import EasyOCRNumberRecogniser
from move_parser_by_replay.util.number_recognisers.MatchTemplateNumberRecogniser import MatchTemplateNumberRecogniser
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface


class InputDisplayObservationManager:
    window_to_stop_searching: int
    maximum_frame_to_look_at: int

    number_recognisers: List[NumberRecogniserInterface]
    button_recogniser: MatchTemplateButtonRecogniser
    direction_recogniser: MatchTemplateDirectionRecogniser

    observations: Dict[int, InputDisplayObservation]
    frame_numbers: List[int]
    merged_display_rows: List[InputDisplayRow]
    video: Video

    def __init__(self, numbers_template: Dict[str, Number], buttons_template: Dict[str, Button],
                 directions_template: Dict[str, Direction], video: Video):
        self.number_recognisers = []

        self.number_recognisers.append(EasyOCRNumberRecogniser())
        self.number_recognisers.append(MatchTemplateNumberRecogniser(numbers_template))
        self.button_recogniser = MatchTemplateButtonRecogniser(buttons_template)
        self.direction_recogniser = MatchTemplateDirectionRecogniser(directions_template)
        self.window_to_stop_searching = 60
        self.maximum_frame_to_look_at = -1

        self.video = video
        self.observations = {}
        self.frame_numbers = []
        self.merged_display_rows = []

    def set_window_to_stop_searching(self, new_window: int) -> None:
        self.window_to_stop_searching = new_window

    def set_maximum_frame_to_look_at(self, max_frame: int) -> None:
        self.maximum_frame_to_look_at = max_frame

    def get_observations(self) -> Dict[int, InputDisplayObservation]:
        return self.observations

    def analyse_full_video(self) -> None:
        frame_count = self.video.get_frame_count()

        final_frame = frame_count if self.maximum_frame_to_look_at == -1 else self.maximum_frame_to_look_at

        self.apply_observations_in_frame(0)
        self.apply_observations_in_frame(final_frame - 5)
        self.apply_base_observations_in_window(0, final_frame - 1)

        self.merged_display_rows = [row for row in self.merged_display_rows if row != InputDisplayRow.get_empty_row()]

    def apply_base_observations_in_window(self, start_frame: int, end_frame: int) -> None:
        middle_frame = (start_frame + end_frame) // 2

        self.apply_observations_in_frame(middle_frame)

        middle_frame_index = bisect.bisect_left(self.frame_numbers, middle_frame)
        previous_frame = self.frame_numbers[middle_frame_index - 1]
        next_frame = self.frame_numbers[middle_frame_index + 1]

        merged_rows_first_window = MergerForInputDisplayObservations.merge_input_displays(
            self.observations[previous_frame], previous_frame, self.observations[middle_frame], middle_frame,
            Player.FIRST_PLAYER)
        merged_rows_second_window = MergerForInputDisplayObservations.merge_input_displays(
            self.observations[middle_frame], middle_frame, self.observations[next_frame], next_frame,
            Player.FIRST_PLAYER)
        if merged_rows_first_window is not None:
            self.merged_display_rows = DiffLibWrapper.merge_sequences(self.merged_display_rows,
                                                                      merged_rows_first_window)
        if merged_rows_second_window is not None:
            self.merged_display_rows = DiffLibWrapper.merge_sequences(self.merged_display_rows,
                                                                      merged_rows_second_window)

        continue_searching = end_frame - start_frame >= self.window_to_stop_searching
        if continue_searching and merged_rows_first_window is None:
            self.apply_base_observations_in_window(start_frame, middle_frame - 1)
        if continue_searching and merged_rows_second_window is None:
            self.apply_base_observations_in_window(middle_frame + 1, end_frame)

    def apply_observations_in_frame(self, frame_number: int) -> InputDisplayObservation:
        frame = self.video.get_frame_from_position(frame_number)

        self.apply_observations_for_player(frame, Player.FIRST_PLAYER, frame_number)
        self.apply_observations_for_player(frame, Player.SECOND_PLAYER, frame_number)

        bisect.insort(self.frame_numbers, frame_number)

        return self.observations[frame_number]

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
