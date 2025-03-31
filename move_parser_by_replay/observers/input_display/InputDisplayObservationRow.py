from typing import Self

from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.input_display.LikelihoodMapForObservation import LikelihoodMapForObservation


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
            buttons_pressed_observed)
        self.direction_pressed_observed = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(
            direction_pressed_observed)
        self.is_empty = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(is_empty)

    def add_frames_pressed_observation(self, frames_pressed: int, weight: int = 1) -> None:
        self.frames_pressed_observed.add_observation(frames_pressed, weight)

    def add_buttons_pressed_observation(self, buttons_pressed: ListOfButtons, weight: int = 1) -> None:
        self.buttons_pressed_observed.add_observation(buttons_pressed, weight)

    def add_direction_pressed_observation(self, direction_pressed: Direction, weight: int = 1) -> None:
        self.direction_pressed_observed.add_observation(direction_pressed, weight)

    def __eq__(self, other: Self) -> bool:
        return (self.frames_pressed_observed, self.direction_pressed_observed, self.buttons_pressed_observed,
                self.is_empty) == (
        other.frames_pressed_observed, other.direction_pressed_observed, other.buttons_pressed_observed, other.is_empty)

    def __hash__(self) -> int:
        return hash((self.frames_pressed_observed, self.direction_pressed_observed, self.buttons_pressed_observed,
                     self.is_empty))
