from typing import List, Dict, Optional

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.input_display.InputDisplayObservation import InputDisplayObservation
from move_parser_by_replay.util.button_recognisers.MatchTemplateButtonRecogniser import MatchTemplateButtonRecogniser
from move_parser_by_replay.util.direction_recognisers.MatchTemplateDirectionRecogniser import \
    MatchTemplateDirectionRecogniser
from move_parser_by_replay.util.number_recognisers.EasyOCRNumberRecogniser import EasyOCRNumberRecogniser
from move_parser_by_replay.util.number_recognisers.MatchTemplateNumberRecogniser import MatchTemplateNumberRecogniser
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface
from move_parser_by_replay.util.number_recognisers.TesseractNumberRecogniser import TesseractNumberRecogniser


class InputDisplayObservationManager:
    window_to_stop_searching: int

    number_recognisers: List[NumberRecogniserInterface]
    button_recogniser: MatchTemplateButtonRecogniser
    direction_recogniser: MatchTemplateDirectionRecogniser

    observations: Dict[int, Optional[InputDisplayObservation]]
    video: Video

    def __init__(self, numbers_template: Dict[str, Number], buttons_template: Dict[str, Button],
                 directions_template: Dict[str, Direction], video: Video):
        self.number_recognisers = []

        self.number_recognisers.append(EasyOCRNumberRecogniser())
        # self.number_recognisers.append(TesseractNumberRecogniser())
        self.number_recognisers.append(MatchTemplateNumberRecogniser(numbers_template))
        self.button_recogniser = MatchTemplateButtonRecogniser(buttons_template)
        self.direction_recogniser = MatchTemplateDirectionRecogniser(directions_template)
        self.window_to_stop_searching = 60

        self.video = video

        self.initialise_observations()

    def set_window_to_stop_searching(self, new_window: int) -> None:
        self.window_to_stop_searching = new_window

    def get_observations(self) -> Dict[int, Optional[InputDisplayObservation]]:
        return self.observations

    def initialise_observations(self) -> None:
        frame_count = self.video.get_frame_count()
        self.observations = {}

        for i in range(1, frame_count + 1):
            self.observations[i] = None

    def analyse_full_video(self) -> None:
        frame_count = self.video.get_frame_count()

        self.apply_base_observations_in_window(0, frame_count - 1)

    def apply_base_observations_in_window(self, start_frame: int, end_frame: int) -> None:
        middle_frame = (start_frame + end_frame) // 2

        self.apply_observations_in_frame(middle_frame)

        if end_frame - start_frame >= self.window_to_stop_searching:
            self.apply_base_observations_in_window(start_frame, middle_frame - 1)
            self.apply_base_observations_in_window(middle_frame + 1, end_frame)

    def apply_observations_in_frame(self, frame_number: int) -> None:
        frame = self.video.get_frame_from_position(frame_number)

        self.apply_observations_for_player(frame, Player.FIRST_PLAYER, frame_number)
        self.apply_observations_for_player(frame, Player.SECOND_PLAYER, frame_number)

    def apply_observations_for_player(self, frame: Frame, player: Player, frame_number: int) -> None:
        subregion_for_buttons = MatchTemplateButtonRecogniser.get_subregion(frame, player)
        buttons_recognised = self.button_recogniser.search_templates_in_image(subregion_for_buttons)

        if self.observations[frame_number] is None:
            self.observations[frame_number] = InputDisplayObservation(frame_number)

        self.observations[frame_number].add_observation_of_buttons(buttons_recognised, player)

        subregion_for_directions = MatchTemplateDirectionRecogniser.get_subregion(frame, player)
        directions_recognised = self.direction_recogniser.search_templates_in_image(subregion_for_directions)
        self.observations[frame_number].add_observation_of_directions(directions_recognised, player)

        subregion_for_numbers = MatchTemplateNumberRecogniser.get_subregion(frame, player)
        for number_recogniser in self.number_recognisers:
            numbers_recognised = number_recogniser.get_numbers_in_region(subregion_for_numbers)
            self.observations[frame_number].add_observation_of_frames_pressed(numbers_recognised, player)
