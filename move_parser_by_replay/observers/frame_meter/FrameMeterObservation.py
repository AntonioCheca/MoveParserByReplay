from typing import Dict, List, Optional, Self, Callable

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterObservation:
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80
    WINDOW_FOR_PAST_COLUMNS = 20

    frame_meter: List[FrameMeterColumn]

    def __init__(self, frame_meter: Optional[List[FrameMeterColumn]] = None):
        if frame_meter is None:
            self.frame_meter = []
        else:
            self.frame_meter = frame_meter

    def get_frame_meter_list(self) -> List[FrameMeterColumn]:
        return self.frame_meter

    @classmethod
    def fill_from_frame_and_positions(cls, frame: Frame, positions: Dict[Player, List[Position]],
                                      frame_meter_in_match: int) -> Self:
        frame_meter_states: Dict[Player, List[Optional[StateFrameMeterEnum]]] = {}
        for player in positions:
            list_for_player: List[Optional[StateFrameMeterEnum]] = []
            for position in positions[player]:
                # raw_color = frame.get_specific_point(position)
                subregion = frame.get_sub_region_around_specific_point(position, 6, 10)
                color_in_subregion = subregion.get_average_color_in_frame()
                list_for_player.append(color_in_subregion.get_potential_state_frame_meter())
            frame_meter_states[player] = list_for_player

        all_columns = []
        for column_position in range(cls.NUMBER_OF_COLUMNS_IN_FRAME_METER):
            states: List[Optional[StateFrameMeterEnum]] = []
            for player in frame_meter_states:
                states.append(frame_meter_states[player][column_position])
            new_column = FrameMeterColumn(states[0], states[1], column_position, frame_meter_in_match)
            all_columns.append(new_column)
        return cls(all_columns)

    def clean_nothing_frames_from_tail(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_unknown_or_nothing())

    def clean_past_frames(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_past())

    def clean_all_past_and_nothing_frames(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(
            lambda column: column.is_unknown_or_nothing()
        )

        self.frame_meter = [frame_column for frame_column in self.frame_meter if not frame_column.is_past()]

    def move_last_past_frames_to_start(self, frame_meters_in_match: int) -> None:
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
                for column in new_list:
                    column.reduce_frame_meter_in_match()
                new_list.append(FrameMeterColumn.get_end_window_column(frame_meters_in_match))
                new_list.extend(self.frame_meter)
                self.frame_meter = new_list

    def add_end_window_if_we_have_enough_states(self, frame_meters_in_match: int) -> None:
        if len(self.frame_meter) > 0.9 * self.NUMBER_OF_COLUMNS_IN_FRAME_METER:
            self.frame_meter.append(FrameMeterColumn.get_end_window_column(frame_meters_in_match))

    def is_last_column_end_of_window(self) -> bool:
        if len(self.frame_meter) == 0:
            return False
        return self.frame_meter[-1].is_end_of_window()

    def clean_continuous_columns_not_following_boolean_function(self,
                                                                boolean_function: Callable[
                                                                    [FrameMeterColumn],
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
