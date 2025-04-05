import bisect
from typing import List, Dict

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.AbstractBinarySearchObserver import AbstractBinarySearchObserver
from move_parser_by_replay.observers.AbstractSequentialSearchObserver import AbstractSequentialSearchObserver
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation
from move_parser_by_replay.observers.frame_meter.MergerForFrameMeterObservation import MergerForFrameMeterObservation
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


class FrameMeterObserver(AbstractSequentialSearchObserver):
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80

    regions: Dict[Player, Region]
    positions_for_frame_meter_rectangles: Dict[Player, List[Position]]
    observations: Dict[int, FrameMeterObservation]

    def __init__(self, video: Video):
        super().__init__(video)
        self.regions = {
            Player.FIRST_PLAYER: Region(358, 801, 1203, 27),
            Player.SECOND_PLAYER: Region(358, 841, 1203, 27)
        }
        self.positions_for_frame_meter_rectangles = {
            Player.FIRST_PLAYER: [],
            Player.SECOND_PLAYER: []
        }
        self.initialise_positions_for_each_player()
        self.observations = {}

    def initialise_positions_for_each_player(self) -> None:
        for player in self.regions:
            middle_y_for_rectangle = self.regions[player].get_height() // 2 + self.regions[player].get_top_y()
            gap_between_rectangle = self.regions[player].get_width() / self.NUMBER_OF_COLUMNS_IN_FRAME_METER
            middle_of_rectangle_size = gap_between_rectangle / 2
            x_offset = self.regions[player].get_left_x()
            for i in range(self.NUMBER_OF_COLUMNS_IN_FRAME_METER):
                position_to_look_x = x_offset + int(gap_between_rectangle * i + middle_of_rectangle_size)
                position = Position(position_to_look_x, middle_y_for_rectangle)
                self.positions_for_frame_meter_rectangles[player].append(position)

    def apply_specific_observations_in_frame(self, frame_number: int):
        frame = self.get_frame_from_position(frame_number)

        new_observation = FrameMeterObservation.fill_from_frame_and_positions(frame,
                                                                              self.positions_for_frame_meter_rectangles)
        new_observation.clean_all_past_and_nothing_frames()
        self.observations[frame_number] = new_observation

    def get_saved_observation_in_frame(self, frame_number: int) -> FrameMeterObservation:
        return self.observations[frame_number]

    def get_merge_observation_in_two_frames(self, first_frame: int, second_frame: int) -> List[FrameMeterColumn]:
        return MergerForFrameMeterObservation.merge_frame_meters(
            self.observations[first_frame], first_frame, self.observations[second_frame], second_frame
        )
