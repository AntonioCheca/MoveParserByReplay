import numpy as np
import cv2
from typing import Optional, Self
from move_parser_by_replay.base.Region import Region


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

    def get_subregion(self, region: Region) -> Self:
        x1 = max(0, region.get_left_x())
        y1 = max(0, region.get_top_y())
        x2 = min(self.width, region.get_right_x())
        y2 = min(self.height, region.get_bottom_y())

        subregion_data = self.image_data[y1:y2, x1:x2]
        return Frame(subregion_data, self.frame_number)

    def show(self) -> None:
        cv2.imshow(f"Frame {self.frame_number}" if self.frame_number is not None else "Frame", self.image_data)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

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
