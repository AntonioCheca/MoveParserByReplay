from typing import Dict, List, Optional, Self

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn


class FrameMeterObservation:
    frame_meter: Dict[Player, List[FrameMeterColumn]]

    def __init__(self, frame_meter: Optional[Dict[Player, List[FrameMeterColumn]]] = None):
        if frame_meter is None:
            self.frame_meter = {}
        else:
            self.frame_meter = frame_meter

    @classmethod
    def fill_from_frame_and_positions(cls, frame: Frame, positions: Dict[Player, List[Position]]) -> Self:
        frame_meter: Dict[Player, List[FrameMeterColumn]] = {}
        for player in positions:
            list_for_player: list[FrameMeterColumn] = []
            for position in positions[player]:
                raw_color = frame.get_specific_point(position)
                color_frame_meter = ColorFrameMeter(tuple(raw_color))
                list_for_player.append(FrameMeterColumn(color_frame_meter.get_potential_state_frame_meter()))
            frame_meter[player] = list_for_player

        return cls(frame_meter)

    def clean_nothing_frames_from_tail(self) -> None:
        maximum_of_not_cleanable_frames = 0
        for player in self.frame_meter:
            current_list = self.frame_meter[player]
            indices_for_not_cleanable_columns = []
            for index, column in enumerate(current_list):
                if not column.is_unknown_or_nothing():
                    indices_for_not_cleanable_columns.append(index)
            if max(indices_for_not_cleanable_columns) > maximum_of_not_cleanable_frames:
                maximum_of_not_cleanable_frames = max(indices_for_not_cleanable_columns)

        for player in self.frame_meter:
            del self.frame_meter[player][-maximum_of_not_cleanable_frames:]

    def clean_past_frames(self) -> None:
        maximum_of_not_cleanable_frames = 0
        for player in self.frame_meter:
            current_list = self.frame_meter[player]
            indices_for_not_cleanable_columns = []
            for index, column in enumerate(current_list):
                if not column.is_past() and not column.is_unknown_or_nothing():
                    indices_for_not_cleanable_columns.append(index)
            if max(indices_for_not_cleanable_columns) > maximum_of_not_cleanable_frames:
                maximum_of_not_cleanable_frames = max(indices_for_not_cleanable_columns)

        for player in self.frame_meter:
            del self.frame_meter[player][-maximum_of_not_cleanable_frames:]
