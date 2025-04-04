from typing import List, Dict

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation


class FrameMeterObserver:
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80

    regions: Dict[Player, Region]
    video: Video
    final_list_of_frame_meter_column: Dict[Player, List[FrameMeterColumn]]
    positions_for_frame_meter_rectangles: Dict[Player, List[Position]]

    def __init__(self, video: Video):
        self.video = video
        self.regions = {
            Player.FIRST_PLAYER: Region(358, 801, 1203, 27),
            Player.SECOND_PLAYER: Region(358, 841, 1203, 27)
        }
        self.positions_for_frame_meter_rectangles = {
            Player.FIRST_PLAYER: [],
            Player.SECOND_PLAYER: []
        }
        self.initialise_positions_for_each_player()

    def initialise_positions_for_each_player(self) -> None:
        for player in self.regions:
            middle_y_for_rectangle = self.regions[player].get_height() // 2 + self.regions[player].get_bottom_y()
            gap_between_rectangle = self.regions[player].get_width() / self.NUMBER_OF_COLUMNS_IN_FRAME_METER
            middle_of_rectangle_size = gap_between_rectangle / 2
            x_offset = self.regions[player].get_left_x()
            for i in range(self.NUMBER_OF_COLUMNS_IN_FRAME_METER):
                position_to_look_x = x_offset + int(gap_between_rectangle * i + middle_of_rectangle_size)
                position = Position(position_to_look_x, middle_y_for_rectangle)
                self.positions_for_frame_meter_rectangles[player].append(position)

    def fill_from_video(self) -> None:
        pass

    def get_list_of_frame_meter_columns_by_frame_position(self, frame_position: int) -> FrameMeterObservation:
        frame = self.video.get_frame_from_position(frame_position)

        frame_meter_observation = FrameMeterObservation.fill_from_frame_and_positions(frame,
                                                                                      self.positions_for_frame_meter_rectangles)
        frame_meter_observation.clean_nothing_frames_from_tail()
        frame_meter_observation.clean_past_frames()

        return frame_meter_observation
