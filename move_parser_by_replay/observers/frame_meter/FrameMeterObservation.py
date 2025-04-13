from typing import Dict, List, Optional, Self, Callable

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.observers.LikelihoodMapForObservation import LikelihoodMapForObservation
from move_parser_by_replay.observers.frame_meter.FrameMeterColumnMap import FrameMeterColumnMap
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter


class FrameMeterObservation:
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80
    WINDOW_FOR_PAST_COLUMNS = 20

    frame_meter: List[FrameMeterColumnMap]

    def __init__(self, frame_meter: Optional[List[FrameMeterColumnMap]] = None):
        if frame_meter is None:
            self.frame_meter = []
        else:
            self.frame_meter = frame_meter

    def get_frame_meter_list(self) -> List[FrameMeterColumnMap]:
        return self.frame_meter

    @classmethod
    def fill_from_frame_and_positions(cls, frame: Frame, positions: Dict[Player, List[Position]]) -> Self:
        frame_meter_states: Dict[Player, List[LikelihoodMapForObservation[StateFrameMeter]]] = {}
        for player in positions:
            list_for_player: List[LikelihoodMapForObservation[StateFrameMeter]] = []
            for position in positions[player]:
                # raw_color = frame.get_specific_point(position)
                subregion = frame.get_sub_region_around_specific_point(position, 10, 20)
                state_in_subregion = subregion.get_map_of_states_in_frame()
                list_for_player.append(state_in_subregion)
            frame_meter_states[player] = list_for_player

        all_columns = []
        for column_position in range(cls.NUMBER_OF_COLUMNS_IN_FRAME_METER):
            states: List[LikelihoodMapForObservation[StateFrameMeter]] = []
            for player in frame_meter_states:
                states.append(frame_meter_states[player][column_position])
            new_column = FrameMeterColumnMap(column_position, states[0], states[1])
            all_columns.append(new_column)
        return cls(all_columns)

    def clean_nothing_frames_from_tail(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_unknown_or_nothing())

    def clean_past_frames(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_past())

    def clean_all_past_and_nothing_frames(self) -> None:
        if len(self.frame_meter) > 0:
            # self.frame_meter = [frame_column for frame_column in self.frame_meter if not frame_column.is_past()]

            self.clean_from_estimated_column_because_it_is_past()
            self.clean_continuous_columns_not_following_boolean_function(
                lambda column: column.is_unknown_or_nothing()
            )

    def clean_from_estimated_column_because_it_is_past(self):
        past_zero_indices = []
        present_zero_indices = []

        for i, frame_column in enumerate(self.frame_meter):
            if frame_column.probability_that_is_past() == 0:
                past_zero_indices.append(i)
            if frame_column.probability_that_is_present() == 0:
                present_zero_indices.append(i)

        min_index = 0
        if past_zero_indices:
            min_index = max(past_zero_indices) + 1

        max_index = len(self.frame_meter)
        if present_zero_indices:
            max_index = min(present_zero_indices)

        if min_index < len(self.frame_meter):
            if min_index > max_index:
                raise ValueError("It seems you are trying to clean a specific observation in "
                                 "Present and Past but the probabilities are contradictory")

            tail_past_probability = 1
            for i in range(min_index, len(self.frame_meter)):
                tail_past_probability *= self.frame_meter[i].probability_that_is_past()

            head_present_probability = 1
            for i in range(min_index):
                head_present_probability *= self.frame_meter[i].probability_that_is_present()

            best_probability = head_present_probability * tail_past_probability
            best_index = min_index

            index_from_which_tail_is_past = min_index + 1
            while index_from_which_tail_is_past <= max_index:
                current_column = self.frame_meter[index_from_which_tail_is_past - 1]

                if current_column.probability_that_is_past() != 0:
                    tail_past_probability /= current_column.probability_that_is_past()
                else:
                    tail_past_probability = 0

                head_present_probability *= current_column.probability_that_is_present()

                current_probability = tail_past_probability * head_present_probability
                if current_probability > best_probability:
                    best_probability = current_probability
                    best_index = index_from_which_tail_is_past

                index_from_which_tail_is_past += 1

            self.frame_meter = self.frame_meter[:best_index]

    def move_last_past_frames_to_start(self) -> None:
        if len(self.frame_meter) != 0:
            window_to_look_in = self.frame_meter[-self.WINDOW_FOR_PAST_COLUMNS:]
            past_frames_from_tail = []
            index = len(window_to_look_in) - 1
            found_present_column = False
            while not found_present_column and index >= 0:
                if window_to_look_in[index].is_past():
                    past_frames_from_tail.append(window_to_look_in[index].transform_from_past_to_present())
                else:
                    found_present_column = True
                index -= 1
            if len(past_frames_from_tail) != 0:
                past_frames_from_tail.reverse()
                new_list = past_frames_from_tail
                new_list.append(FrameMeterColumnMap.get_end_window_column())
                new_list.extend(self.frame_meter)
                self.frame_meter = new_list

    def add_end_window_if_we_have_enough_states(self) -> None:
        if len(self.frame_meter) > 0.9 * self.NUMBER_OF_COLUMNS_IN_FRAME_METER:
            self.frame_meter.append(FrameMeterColumnMap.get_end_window_column())

    def is_last_column_end_of_window(self) -> bool:
        if len(self.frame_meter) == 0:
            return False
        return self.frame_meter[-1].is_end_of_window()

    def clean_continuous_columns_not_following_boolean_function(self,
                                                                boolean_function: Callable[
                                                                    [FrameMeterColumnMap],
                                                                    bool
                                                                ]) -> None:
        maximum_of_not_cleanable_frames = 0
        found = False
        index = len(self.frame_meter) - 1
        while not found and index >= 0:
            if not boolean_function(self.frame_meter[index]):
                found = True
                maximum_of_not_cleanable_frames = index
            index -= 1

        if not found:
            del self.frame_meter[0:]
        else:
            del self.frame_meter[maximum_of_not_cleanable_frames + 1:]
