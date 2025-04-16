from abc import abstractmethod, ABC
from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Video import Video


class AbstractSequentialSearchObserver(ABC):
    DEFAULT_GAP_SIZE = 20
    FRAMES_TO_REMOVE_FROM_TAIL_FOR_NUMBERS = 0

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
    def get_exact_list_from_frame(self, frame_number: int):
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

        last_frame_changed = 0
        for frame_number in frames_to_look:
            is_first_column_from_list_to_merge_0 = False
            self.apply_observations_in_frame(frame_number)
            # merged_list = self.get_merge_observation_in_two_frames(frame_number - self.gap_size, frame_number)
            list_to_merge = self.get_exact_list_from_frame(frame_number)
            previous_length = len(self.exact_final_list)
            if len(list_to_merge) > 0:
                is_first_column_from_list_to_merge_0 = list_to_merge[0].get_column_position() == 0
            self.exact_final_list[-len(list_to_merge):] = self.merge_two_sequences(
                self.exact_final_list[-len(list_to_merge):], list_to_merge, frame_number - last_frame_changed,
                is_first_column_from_list_to_merge_0)
            self.update_internal_variables_if_needed()
            if previous_length != len(self.exact_final_list):
                last_frame_changed = frame_number

        self.clean_final_list_if_needed()

    def clean_final_list_if_needed(self) -> None:
        pass

    def update_internal_variables_if_needed(self) -> None:
        pass

    @abstractmethod
    def merge_two_sequences(self, first_sequence: List, second_sequence: List, last_change_in_frames: int,
                            is_new_sequence: bool) -> List:
        pass
