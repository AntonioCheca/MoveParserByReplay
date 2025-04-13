from typing import Self

from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.observers.LikelihoodMapForObservation import LikelihoodMapForObservation


class InputDisplayObservationRow:
    frames_pressed_observed: LikelihoodMapForObservation[int]
    buttons_pressed_observed: LikelihoodMapForObservation[ListOfButtons]
    direction_pressed_observed: LikelihoodMapForObservation[Direction]
    is_empty: LikelihoodMapForObservation[bool]

    def __init__(self, frames_pressed_observed: LikelihoodMapForObservation[int] = None,
                 buttons_pressed_observed: LikelihoodMapForObservation[ListOfButtons] = None,
                 direction_pressed_observed: LikelihoodMapForObservation[Direction] = None,
                 is_empty: LikelihoodMapForObservation[bool] = None):
        self.frames_pressed_observed = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(
            frames_pressed_observed)
        self.buttons_pressed_observed = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(
            buttons_pressed_observed, default_value=ListOfButtons([]))
        self.direction_pressed_observed = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(
            direction_pressed_observed)
        self.is_empty = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(is_empty)

    def get_probability_this_is_same_row_than(self, other: Self) -> float:
        frames_pressed_equal_probability = self.frames_pressed_observed.get_probability_this_object_is_the_same_than(
            other.frames_pressed_observed
        )
        buttons_pressed_equal_probability = self.buttons_pressed_observed.get_probability_this_object_is_the_same_than(
            other.buttons_pressed_observed
        )
        direction_pressed_equal_probability = \
            self.direction_pressed_observed.get_probability_this_object_is_the_same_than(
                other.direction_pressed_observed
            )

        return frames_pressed_equal_probability * \
            buttons_pressed_equal_probability * \
            direction_pressed_equal_probability

    def get_best_possibility(self) -> InputDisplayRow:
        best_frames = self.frames_pressed_observed.get_known_most_likely_possibility()
        best_buttons = self.buttons_pressed_observed.get_known_most_likely_possibility()
        best_direction = self.direction_pressed_observed.get_known_most_likely_possibility()

        return InputDisplayRow(best_direction, best_buttons, best_frames)

    def get_best_possibility_merging_with_second_row(self, second_row: Self) -> InputDisplayRow:
        merged_frames = self.frames_pressed_observed.get_best_possibility_according_to_second_map(
            second_row.frames_pressed_observed)
        merged_buttons = self.buttons_pressed_observed.get_best_possibility_according_to_second_map(
            second_row.buttons_pressed_observed)
        merged_direction = self.direction_pressed_observed.get_best_possibility_according_to_second_map(
            second_row.direction_pressed_observed)

        return InputDisplayRow(merged_direction, merged_buttons, merged_frames)

    def add_frames_pressed_observation(self, frames_pressed: int, weight: int = 1) -> None:
        self.frames_pressed_observed.add_observation(frames_pressed, weight)

    def add_buttons_pressed_observation(self, buttons_pressed: ListOfButtons, weight: int = 1) -> None:
        self.buttons_pressed_observed.add_observation(buttons_pressed, weight)

    def add_direction_pressed_observation(self, direction_pressed: Direction, weight: int = 1) -> None:
        self.direction_pressed_observed.add_observation(direction_pressed, weight)

    def __eq__(self, other: Self) -> bool:
        return (self.frames_pressed_observed, self.direction_pressed_observed, self.buttons_pressed_observed,
                self.is_empty) == (
            other.frames_pressed_observed, other.direction_pressed_observed, other.buttons_pressed_observed,
            other.is_empty)

    def __hash__(self) -> int:
        return hash((self.frames_pressed_observed, self.direction_pressed_observed, self.buttons_pressed_observed,
                     self.is_empty))

    def is_likely_empty(self) -> bool:
        return self.frames_pressed_observed.get_known_most_likely_possibility() is None and \
            self.direction_pressed_observed.get_known_most_likely_possibility() is None
