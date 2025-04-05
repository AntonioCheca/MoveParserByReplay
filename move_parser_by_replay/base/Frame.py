import numpy as np
import cv2
from typing import Optional, Self

from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class Frame:
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
