import bisect
from abc import abstractmethod, ABC
from typing import List

from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


class AbstractBinarySearchObserver(ABC):
    window_to_stop_searching: int
    maximum_frame_to_look_at: int
    frame_numbers: List[int]
    exact_final_list: List
    video: Video

    def __init__(self, video: Video):
        self.window_to_stop_searching = 60
        self.maximum_frame_to_look_at = -1
        self.frame_numbers = []
        self.exact_final_list = []
        self.video = video

    def get_exact_final_list(self) -> List:
        return self.exact_final_list

    def set_window_to_stop_searching(self, new_window: int) -> None:
        self.window_to_stop_searching = new_window

    def set_maximum_frame_to_look_at(self, max_frame: int) -> None:
        self.maximum_frame_to_look_at = max_frame

    def apply_observations_in_frame(self, frame_number: int):
        self.apply_specific_observations_in_frame(frame_number)

        bisect.insort(self.frame_numbers, frame_number)

        return self.get_saved_observation_in_frame(frame_number)

    @abstractmethod
    def apply_specific_observations_in_frame(self, frame_number: int):
        pass

    @abstractmethod
    def get_saved_observation_in_frame(self, frame_number: int):
        pass

    def apply_base_observations_in_window(self, start_frame: int, end_frame: int) -> None:
        middle_frame = (start_frame + end_frame) // 2

        self.apply_observations_in_frame(middle_frame)

        middle_frame_index = bisect.bisect_left(self.frame_numbers, middle_frame)
        previous_frame = self.frame_numbers[middle_frame_index - 1]
        next_frame = self.frame_numbers[middle_frame_index + 1]

        merged_list_first_window = self.get_merge_observation_in_two_frames(previous_frame, middle_frame)
        merged_list_second_window = self.get_merge_observation_in_two_frames(middle_frame, next_frame)
        if merged_list_first_window is not None:
            self.exact_final_list = DiffLibWrapper.merge_sequences(self.exact_final_list,
                                                                   merged_list_first_window)
        if merged_list_second_window is not None:
            self.exact_final_list = DiffLibWrapper.merge_sequences(self.exact_final_list,
                                                                   merged_list_second_window)

        continue_searching = end_frame - start_frame >= self.window_to_stop_searching
        if continue_searching and merged_list_first_window is None:
            self.apply_base_observations_in_window(start_frame, middle_frame - 1)
        if continue_searching and merged_list_second_window is None:
            self.apply_base_observations_in_window(middle_frame + 1, end_frame)

    @abstractmethod
    def get_merge_observation_in_two_frames(self, first_frame: int, second_frame: int) -> List:
        pass

    def analyse_full_video(self) -> None:
        frame_count = self.video.get_frame_count()

        final_frame = frame_count if self.maximum_frame_to_look_at == -1 else self.maximum_frame_to_look_at

        self.apply_observations_in_frame(0)
        self.apply_observations_in_frame(final_frame - 5)
        self.apply_base_observations_in_window(0, final_frame - 1)

        self.clean_final_list_if_needed()

    def clean_final_list_if_needed(self) -> None:
        pass
