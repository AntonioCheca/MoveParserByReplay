from typing import List, Dict, Tuple

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.AbstractSequentialSearchObserver import AbstractSequentialSearchObserver
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation
from move_parser_by_replay.observers.frame_meter.MergerForFrameMeterObservation import MergerForFrameMeterObservation
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from move_parser_by_replay.observers.frame_meter.StateType import StateType


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
            offset_y = 12
            final_y = middle_y_for_rectangle + offset_y
            gap_between_rectangle = self.regions[player].get_width() / self.NUMBER_OF_COLUMNS_IN_FRAME_METER
            middle_of_rectangle_size = gap_between_rectangle / 2
            x_offset = self.regions[player].get_left_x()
            for i in range(self.NUMBER_OF_COLUMNS_IN_FRAME_METER):
                position_to_look_x = x_offset + int(gap_between_rectangle * i + middle_of_rectangle_size)
                position = Position(position_to_look_x, middle_y_for_rectangle)
                self.positions_for_frame_meter_rectangles[player].append(position)

    def apply_specific_observations_in_frame(self, frame_number: int) -> None:
        frame = self.get_frame_from_position(frame_number)

        new_observation = FrameMeterObservation.fill_from_frame_and_positions(frame,
                                                                              self.positions_for_frame_meter_rectangles)

        new_observation.clean_nothing_frames_from_tail()
        new_observation.move_last_past_frames_to_start()
        new_observation.clean_all_past_and_nothing_frames()
        new_observation.add_end_window_if_we_have_enough_states()
        self.observations[frame_number] = new_observation

    def get_saved_observation_in_frame(self, frame_number: int) -> FrameMeterObservation:
        return self.observations[frame_number]

    def get_exact_list_from_frame(self, frame_number: int) -> List[FrameMeterColumn]:
        return self.get_saved_observation_in_frame(frame_number).get_frame_meter_list()

    def get_merge_observation_in_two_frames(self, first_frame: int, second_frame: int) -> List[FrameMeterColumn]:
        return MergerForFrameMeterObservation.merge_frame_meters(
            self.observations[first_frame], first_frame, self.observations[second_frame], second_frame
        )

    def clean_final_list_if_needed(self) -> None:
        self.exact_final_list: List[FrameMeterColumn]

        self.exact_final_list: List[FrameMeterColumn] = [column for column in self.exact_final_list if
                                                         not column.is_end_of_window()]
        players = [Player.FIRST_PLAYER, Player.SECOND_PLAYER]

        for player in players:
            self.clean_final_list_if_needed_for_player(player)

    def merge_two_sequences(self, first_sequence: List[FrameMeterColumn], second_sequence: List[FrameMeterColumn]) -> \
            List[FrameMeterColumn]:
        if len(first_sequence) == 0:
            return second_sequence
        if len(second_sequence) == 0:
            return first_sequence

        new_list: List[FrameMeterColumn] = []

        start_overlap_position = second_sequence[0].get_column_position()

        first_index = 0

        while first_index < len(first_sequence) and \
                first_sequence[first_index].get_column_position() < start_overlap_position:
            new_list.append(first_sequence[first_index])
            first_index += 1

        second_index = 0

        while first_index < len(first_sequence) and second_index < len(second_sequence):
            first_position = first_sequence[first_index].get_column_position()
            second_position = second_sequence[second_index].get_column_position()

            if first_position == second_position:
                merged_column = first_sequence[first_index].merge_with_other_column(second_sequence[second_index])
                new_list.append(merged_column)
                first_index += 1
                second_index += 1
            elif first_position < second_position:
                new_list.append(first_sequence[first_index])
                first_index += 1
            else:
                new_list.append(second_sequence[second_index])
                second_index += 1

        while first_index < len(first_sequence):
            new_list.append(first_sequence[first_index])
            first_index += 1

        while second_index < len(second_sequence):
            new_list.append(second_sequence[second_index])
            second_index += 1

        return new_list

    def clean_final_list_if_needed_for_player(self, player: Player) -> None:
        self.overwrite_full_invulnerability_frames_if_they_are_sparse(player)

    @staticmethod
    def get_best_guess_from_list_of_columns(list_of_columns: List[FrameMeterColumn]) -> FrameMeterColumn:
        filtered_list = [column for column in list_of_columns if
                         not column.is_past() and not column.is_unknown_or_nothing()]
        if len(filtered_list) > 0:
            return filtered_list[0]
        return list_of_columns[0]

    def overwrite_full_invulnerability_frames_if_they_are_sparse(self, player: Player):
        self.exact_final_list: List[FrameMeterColumn]
        list_of_full_invulnerability_states: List[int] = []
        threshold_for_invulnerability_frames_that_cannot_be_alone = 3
        continuous_invulnerability_frames = 0
        for index, column in enumerate(self.exact_final_list):
            state = column.get_state_for_player(player)
            most_likely_possibility = state.get_most_likely_possibility()
            if most_likely_possibility is not None and most_likely_possibility.get_state_type() in [
                StateType.FULL_INVULNERABILITY_1,
                StateType.FULL_INVULNERABILITY_2
            ]:
                continuous_invulnerability_frames += 1
            else:
                if 0 < continuous_invulnerability_frames <= threshold_for_invulnerability_frames_that_cannot_be_alone:
                    list_of_full_invulnerability_states.extend(range(index - continuous_invulnerability_frames, index))
                continuous_invulnerability_frames = 0
        for index in list_of_full_invulnerability_states:
            previous_state_to_copy = self.exact_final_list[index - 1].get_state_for_player(player)
            self.exact_final_list[index].set_state_for_player(player, previous_state_to_copy)

    def get_exact_list_for_player_as_frame_count(self, player: Player) -> List[Tuple[StateFrameMeter, int]]:
        self.exact_final_list: List[FrameMeterColumn]
        list_of_states_by_frames: List[Tuple[StateFrameMeter, int]] = []

        continuous_state_frames = 0
        current_state = None
        for column in self.exact_final_list:
            new_state = column.get_state_for_player(player).get_most_likely_possibility()
            if new_state == current_state:
                continuous_state_frames += 1
            else:
                list_of_states_by_frames.append((current_state, continuous_state_frames))
                continuous_state_frames = 1
                current_state = new_state
        list_of_states_by_frames.append((current_state, continuous_state_frames))

        return list_of_states_by_frames
