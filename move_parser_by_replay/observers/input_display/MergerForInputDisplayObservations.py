from typing import Optional, List

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.observers.input_display.InputDisplayObservation import InputDisplayObservation
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow


class MergerForInputDisplayObservations:
    THRESHOLD_TO_START_CHECKING_OVERLAPS = 150

    @staticmethod
    def merge_input_displays(first_input: InputDisplayObservation, first_frame: int,
                             second_input: InputDisplayObservation, second_frame: int, player: Player) -> \
            Optional[List[InputDisplayRow]]:
        if second_frame - first_frame > MergerForInputDisplayObservations.THRESHOLD_TO_START_CHECKING_OVERLAPS:
            return None

        for slide_possibilities in range(0, InputDisplayObservation.MAX_ROWS_TO_OBSERVE):
            is_slided = first_input.is_observation_inside_other_observation_slided_n_rows(second_input,
                                                                                          slide_possibilities,
                                                                                          player)
            if is_slided:
                return MergerForInputDisplayObservations.get_final_list_of_rows_from_input_displays_slided(first_input,
                                                                                                           second_input,
                                                                                                           player,
                                                                                                           slide_possibilities)

        return None

    @staticmethod
    def get_final_list_of_rows_from_input_displays_slided(first_input: InputDisplayObservation,
                                                          second_input: InputDisplayObservation,
                                                          player: Player,
                                                          slided_rows: int) -> List[InputDisplayRow]:
        max_rows = InputDisplayObservation.MAX_ROWS_TO_OBSERVE
        overlapped_rows_number = max_rows - slided_rows - 1
        list_of_input_rows: List[InputDisplayRow] = []

        keys_first_no_overlap = list(range(max_rows, overlapped_rows_number, -1))
        first_input_rows_without_overlap = first_input.get_observation_rows_by_list_of_ints_and_player(player,
                                                                                                       keys_first_no_overlap)
        keys_second_no_overlap = list(range(1 + slided_rows, 1, -1))
        second_input_rows_without_overlap = second_input.get_observation_rows_by_list_of_ints_and_player(player,
                                                                                                         keys_second_no_overlap)

        keys_first_overlap = list(range(overlapped_rows_number + 1, 1, -1))
        overlapped_first_rows = first_input.get_observation_rows_by_list_of_ints_and_player(player, keys_first_overlap)
        keys_second_overlap = list(range(max_rows, 1 + slided_rows, -1))
        overlapped_second_rows = second_input.get_observation_rows_by_list_of_ints_and_player(player,
                                                                                              keys_second_overlap)

        for first_observation in first_input_rows_without_overlap:
            list_of_input_rows.append(first_observation.get_best_possibility())

        final_overlap_rows = []
        for key in range(overlapped_rows_number):
            first_overlap = overlapped_first_rows[key]
            second_overlap = overlapped_second_rows[key]
            final_overlap_rows.append(first_overlap.get_best_possibility_merging_with_second_row(second_overlap))

        list_of_input_rows.extend(final_overlap_rows)

        for second_observation in second_input_rows_without_overlap:
            list_of_input_rows.append(second_observation.get_best_possibility())

        return list_of_input_rows
