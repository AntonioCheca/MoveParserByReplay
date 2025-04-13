import numpy as np
from typing import Optional, Self, Dict

from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.observers.LikelihoodMapForObservation import LikelihoodMapForObservation
from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from move_parser_by_replay.observers.frame_meter.StateFrameMeterRegistry import StateFrameMeterRegistry
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class Frame:
    MINIMAL_PERCENTAGE_OF_PIXELS_TO_ACCOUNT_FOR_FRAME_VALUE = 0
    image_data: np.ndarray
    frame_number: Optional[int]
    height: int
    width: int

    def __init__(self, frame_data: np.ndarray, frame_number: Optional[int] = None):
        self.image_data = frame_data
        self.frame_number = frame_number
        self.height, self.width = frame_data.shape[:2]

    def shape(self) -> tuple:
        return self.image_data.shape

    def get_frame_number(self) -> int:
        return self.frame_number

    def get_height(self) -> int:
        return self.height

    def get_image_data(self) -> np.ndarray:
        return self.image_data

    def get_specific_point(self, position: Position) -> np.ndarray:
        return self.image_data[position.get_y(), position.get_x()]

    def get_subregion(self, region: Region) -> Self:
        x1 = max(0, region.get_left_x())
        y1 = max(0, region.get_top_y())
        x2 = min(self.width, region.get_right_x())
        y2 = min(self.height, region.get_bottom_y())

        subregion_data = self.image_data[y1:y2, x1:x2]
        return Frame(subregion_data, self.frame_number)

    def get_sub_region_around_specific_point(self, point: Position, width: int, height: int) -> Self:
        region = Region(point.get_x() - width // 2, point.get_y() - height // 2, width, height)
        return self.get_subregion(region)

    def get_average_color_in_frame(self) -> ColorFrameMeter:
        color_as_tuple = tuple(np.average(self.image_data, axis=(0, 1)))
        return ColorFrameMeter(color_as_tuple)

    def get_map_of_states_in_frame(self) -> LikelihoodMapForObservation[StateFrameMeter]:
        states_detected: Dict[StateFrameMeter, int] = {}
        for row in self.image_data:
            for pixel in row:
                color = ColorFrameMeter(tuple(pixel))
                state = color.get_potential_state_frame_meter()
                if state is None:
                    weight_of_observation = 1
                else:
                    weight_of_observation = StateFrameMeterRegistry.get_weight(state.get_state_type(),
                                                                               state.get_temporal_state())
                if state in states_detected:
                    states_detected[state] += weight_of_observation
                else:
                    states_detected[state] = weight_of_observation

        likelihood_map = LikelihoodMapForObservation(total_weight=0)
        for state, count in states_detected.items():
            likelihood_map.add_observation(state, weight=count)
        if likelihood_map.get_total_weight() == 0:
            likelihood_map.add_observation(None, 1)
        return likelihood_map

    def show(self) -> None:
        OpenCVWrapper.show_image(self.image_data)

    def get_left_region(self) -> Self:
        left_digit_width = self.width // 2
        left_region = Region(0, 0, left_digit_width, self.height)
        left_digit_frame = self.get_subregion(left_region)
        return left_digit_frame

    def get_right_region(self) -> Self:
        left_digit_width = self.width // 2
        right_region = Region(left_digit_width, 0, left_digit_width, self.height)
        right_digit_frame = self.get_subregion(right_region)
        return right_digit_frame
