import cv2
import os
from typing import Iterator, Optional, List, Dict
from move_parser_by_replay.base.Frame import Frame


def validate_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


class Video:
    file_path: str
    capture: cv2.VideoCapture
    frame_count: int
    fps: float
    width: int
    height: int
    duration: float

    def __init__(self, file_path: str):
        self.file_path = file_path

        validate_file_exists(file_path)

        self.capture = cv2.VideoCapture(file_path)
        if not self.capture.isOpened():
            raise ValueError(f"Could not open video file: {file_path}")

        self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0

    def get_frame_from_position(self, frame_number: int) -> Optional[Frame]:
        if frame_number < 0 or frame_number >= self.frame_count:
            return None

        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        success, frame_data = self.capture.read()
        if not success:
            return None

        return Frame(frame_data, frame_number)

    def get_frames_as_iterator(self) -> Iterator[Frame]:
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        frame_number = 0
        still_reading = True
        while still_reading:
            still_reading, frame_data = self.capture.read()

            if still_reading:
                yield Frame(frame_data, frame_number)
                frame_number += 1

    def get_frames_from_static_list(self, needed_frames: List[int]) -> Dict[int, Frame]:
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        frame_number = 0
        still_reading = True
        dict_of_frames = {}
        max_frame = max(needed_frames)
        while still_reading and frame_number <= max_frame:
            still_reading, frame_data = self.capture.read()

            if still_reading and frame_number in needed_frames:
                dict_of_frames[frame_number] = Frame(frame_data, frame_number)
            frame_number += 1
        return dict_of_frames

    def get_frame_count(self) -> int:
        return self.frame_count

    def __del__(self):
        if hasattr(self, 'capture'):
            self.capture.release()
