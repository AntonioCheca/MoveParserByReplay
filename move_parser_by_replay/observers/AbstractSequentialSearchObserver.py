import bisect
from abc import abstractmethod, ABC
from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


class AbstractSequentialSearchObserver(ABC):
    DEFAULT_GAP_SIZE = 20

    gap_size: int
    maximum_frame_to_look_at: int
    frames: Dict[int, Frame]
    exact_final_list: List
    video: Video

    def __init__(self, video: Video, gap_size: int = DEFAULT_GAP_SIZE):
        self.gap_size = gap_size
        self.maximum_frame_to_look_at = -1
        self.exact_final_list = []
        self.video = video
        self.frames = {}

    def get_exact_final_list(self) -> List:
        return self.exact_final_list

    def set_maximum_frame_to_look_at(self, max_frame: int) -> None:
        self.maximum_frame_to_look_at = max_frame

    def apply_observations_in_frame(self, frame_number: int):
        self.apply_specific_observations_in_frame(frame_number)

        return self.get_saved_observation_in_frame(frame_number)

    @abstractmethod
    def apply_specific_observations_in_frame(self, frame_number: int):
        pass

    @abstractmethod
    def get_saved_observation_in_frame(self, frame_number: int):
        pass

    @abstractmethod
    def get_merge_observation_in_two_frames(self, first_frame: int, second_frame: int) -> List:
        pass

    def get_frame_from_position(self, frame_number: int) -> Frame:
        return self.frames[frame_number]

    def analyse_full_video(self) -> None:
        frame_count = self.video.get_frame_count()

        final_frame = frame_count if self.maximum_frame_to_look_at == -1 else self.maximum_frame_to_look_at

        frames_to_look = [self.gap_size * i for i in range(0, (final_frame - 5) // self.gap_size)]

        self.frames = self.video.get_frames_from_static_list(frames_to_look)

        for frame_number in frames_to_look:
            self.apply_observations_in_frame(frame_number)
            if frame_number != 0:
                merged_list = self.get_merge_observation_in_two_frames(frame_number - self.gap_size, frame_number)
                self.exact_final_list = DiffLibWrapper.merge_sequences(self.exact_final_list, merged_list)

        self.clean_final_list_if_needed()

    def clean_final_list_if_needed(self) -> None:
        pass
