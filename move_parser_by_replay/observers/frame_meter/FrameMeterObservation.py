from typing import Dict, List, Optional, Self, Callable

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterObservation:
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80

    frame_meter: List[FrameMeterColumn]

    def __init__(self, frame_meter: Optional[List[FrameMeterColumn]] = None):
        if frame_meter is None:
            self.frame_meter = []
        else:
            self.frame_meter = frame_meter

    def get_frame_meter_list(self) -> List[FrameMeterColumn]:
        return self.frame_meter

    @classmethod
    def fill_from_frame_and_positions(cls, frame: Frame, positions: Dict[Player, List[Position]]) -> Self:
        frame_meter_states: Dict[Player, List[Optional[StateFrameMeterEnum]]] = {}
        for player in positions:
            list_for_player: List[Optional[StateFrameMeterEnum]] = []
            for position in positions[player]:
                raw_color = frame.get_specific_point(position)
                subregion = frame.get_sub_region_around_specific_point(position, 200, 200)
                color_frame_meter = ColorFrameMeter(tuple(raw_color))
                list_for_player.append(color_frame_meter.get_potential_state_frame_meter())
            frame_meter_states[player] = list_for_player

        all_columns = []
        for i in range(cls.NUMBER_OF_COLUMNS_IN_FRAME_METER):
            states: List[Optional[StateFrameMeterEnum]] = []
            for player in frame_meter_states:
                states.append(frame_meter_states[player][i])
            new_column = FrameMeterColumn(*states)
            all_columns.append(new_column)
        return cls(all_columns)

    def clean_nothing_frames_from_tail(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_unknown_or_nothing())

    def clean_past_frames(self) -> None:
        self.clean_continuous_columns_not_following_boolean_function(lambda column: column.is_past())

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
