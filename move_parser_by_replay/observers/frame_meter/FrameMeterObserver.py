from typing import List, Dict, Tuple

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.AbstractSequentialSearchObserver import AbstractSequentialSearchObserver
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation
from move_parser_by_replay.observers.frame_meter.MergerForFrameMeterObservation import MergerForFrameMeterObservation
from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterObserver(AbstractSequentialSearchObserver):
    NUMBER_OF_COLUMNS_IN_FRAME_METER = 80

    regions: Dict[Player, Region]
    positions_for_frame_meter_rectangles: Dict[Player, List[Position]]
    observations: Dict[int, FrameMeterObservation]
    frame_meters_passed: int

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
        self.frame_meters_passed = 0

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
                                                                              self.positions_for_frame_meter_rectangles,
                                                                              self.frame_meters_passed)

        new_observation.clean_nothing_frames_from_tail()
        new_observation.move_last_past_frames_to_start(self.frame_meters_passed)
        new_observation.clean_all_past_and_nothing_frames()
        new_observation.add_end_window_if_we_have_enough_states(self.frame_meters_passed)
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
        players = [Player.FIRST_PLAYER, Player.SECOND_PLAYER]

        for player in players:
            self.clean_final_list_if_needed_for_player(player)

    def update_internal_variables_if_needed(self) -> None:
        self.frame_meters_passed = 0
        for column in self.exact_final_list:
            if column.is_end_of_window():
                self.frame_meters_passed += 1

    def clean_final_list_if_needed_for_player(self, player: Player) -> None:
        self.exact_final_list: List[FrameMeterColumn]

        self.exact_final_list: List[FrameMeterColumn] = [column for column in self.exact_final_list if
                                                         not column.is_end_of_window()]
        self.exact_final_list: List[FrameMeterColumn] = [column for column in self.exact_final_list if
                                                         not column.is_past()]

        self.overwrite_nones_by_previous_continuous_state(player)

        self.overwrite_full_invulnerability_frames_if_they_are_sparse(player)

        self.remove_duplicities_from_same_column_number_in_final_list()

    def remove_duplicities_from_same_column_number_in_final_list(self) -> None:
        dict_summary = self.get_dict_summary_from_final_list()
        max_frame_meter = self.get_max_frame_meter()
        final_list: List[FrameMeterColumn] = []
        for frame_meter_count in range(max_frame_meter):
            max_column_in_this_frame_meter = self.get_max_column_in_frame_meter(frame_meter_count)
            for column_number in range(max_column_in_this_frame_meter):
                key_in_dict = (frame_meter_count, column_number)
                if key_in_dict in dict_summary:
                    list_of_columns = dict_summary[key_in_dict]
                    final_list.append(self.get_best_guess_from_list_of_columns(list_of_columns))
                elif (frame_meter_count, column_number - 1) in dict_summary:
                    list_of_columns = dict_summary[(frame_meter_count, column_number - 1)]
                    final_list.append(self.get_best_guess_from_list_of_columns(list_of_columns))
                else:
                    final_list.append(
                        FrameMeterColumn(StateFrameMeterEnum.NOTHING, StateFrameMeterEnum.NOTHING, column_number,
                                         frame_meter_count))
        self.exact_final_list = final_list

    def get_max_column_in_frame_meter(self, frame_meter_count: int) -> int:
        max_column_in_this_frame_meter = 0
        for column in self.exact_final_list:
            if column.get_frame_meter_in_match() == frame_meter_count and column.get_column_position() > max_column_in_this_frame_meter:
                max_column_in_this_frame_meter = column.get_column_position()
        return max_column_in_this_frame_meter

    @staticmethod
    def get_best_guess_from_list_of_columns(list_of_columns: List[FrameMeterColumn]) -> FrameMeterColumn:
        filtered_list = [column for column in list_of_columns if
                         not column.is_past() and not column.is_unknown_or_nothing()]
        if len(filtered_list) > 0:
            return filtered_list[0]
        return list_of_columns[0]

    def get_max_frame_meter(self) -> int:
        max_frame_meter = 0
        for column in self.exact_final_list:
            if column.get_frame_meter_in_match() > max_frame_meter:
                max_frame_meter = column.get_frame_meter_in_match()
        return max_frame_meter

    def get_dict_summary_from_final_list(self) -> Dict[Tuple[int, int], List[FrameMeterColumn]]:
        dict_summary: Dict[Tuple[int, int], List[FrameMeterColumn]] = {}
        for column in self.exact_final_list:
            key_in_dict = (column.get_frame_meter_in_match(), column.get_column_position())
            if key_in_dict not in dict_summary:
                dict_summary[key_in_dict] = []
            dict_summary[key_in_dict].append(column)
        return dict_summary

    def overwrite_full_invulnerability_frames_if_they_are_sparse(self, player: Player):
        self.exact_final_list: List[FrameMeterColumn]
        list_of_full_invulnerability_states: List[int] = []
        threshold_for_invulnerability_frames_that_cannot_be_alone = 3
        continuous_invulnerability_frames = 0
        for index, column in enumerate(self.exact_final_list):
            state = column.get_state_for_player(player)
            if state == StateFrameMeterEnum.FULL_INVULNERABILITY_1:
                continuous_invulnerability_frames += 1
            else:
                if 0 < continuous_invulnerability_frames <= threshold_for_invulnerability_frames_that_cannot_be_alone:
                    list_of_full_invulnerability_states.extend(range(index - continuous_invulnerability_frames, index))
                continuous_invulnerability_frames = 0
        for index in list_of_full_invulnerability_states:
            previous_state_to_copy = self.exact_final_list[index - 1].get_state_for_player(player)
            self.exact_final_list[index].set_state_for_player(player, previous_state_to_copy)

    def overwrite_nones_by_previous_continuous_state(self, player: Player) -> None:
        current_state = self.exact_final_list[0].get_state_for_player(player)
        continuous_length = 1
        overwriting_nones = False
        amount_to_overwrite = 0
        amount_nones_overwritten = 0
        for i in range(len(self.exact_final_list)):
            overwrite_with_current_state = False
            new_state = self.exact_final_list[i].get_state_for_player(player)
            if new_state == current_state:
                continuous_length += 1
                if new_state is None and overwriting_nones:
                    overwrite_with_current_state = True
                    amount_nones_overwritten += 1
                    if amount_nones_overwritten >= amount_to_overwrite:
                        overwriting_nones = False
                        amount_to_overwrite = 0
                        amount_nones_overwritten = 0
            elif new_state is None:
                if current_state.cannot_be_followed_by_none():
                    overwrite_with_current_state = True
                elif continuous_length >= 3:
                    overwriting_nones = True
                    if continuous_length >= 97:
                        amount_to_overwrite = 3
                        overwrite_with_current_state = True
                        amount_nones_overwritten = 1
                    elif continuous_length >= 8:
                        amount_to_overwrite = 2
                        overwrite_with_current_state = True
                        amount_nones_overwritten = 1
                    else:
                        amount_to_overwrite = 0
                        amount_nones_overwritten = 0
                        overwriting_nones = False
            else:
                amount_to_overwrite = 0
                amount_nones_overwritten = 0
                overwriting_nones = False
            if overwrite_with_current_state:
                self.exact_final_list[i].set_state_for_player(player, current_state)
            current_state = self.exact_final_list[i].get_state_for_player(player)

    def get_exact_list_for_player_as_frame_count(self, player: Player) -> List[Tuple[StateFrameMeterEnum, int]]:
        self.exact_final_list: List[FrameMeterColumn]
        list_of_states_by_frames: List[Tuple[StateFrameMeterEnum, int]] = []

        continuous_state_frames = 0
        current_state = None
        for column in self.exact_final_list:
            new_state = column.get_state_for_player(player)
            if new_state == current_state:
                continuous_state_frames += 1
            else:
                list_of_states_by_frames.append((current_state, continuous_state_frames))
                continuous_state_frames = 1
                current_state = new_state
        list_of_states_by_frames.append((current_state, continuous_state_frames))

        return list_of_states_by_frames
