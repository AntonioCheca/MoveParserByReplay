from typing import List

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterColumnMap import FrameMeterColumnMap
from move_parser_by_replay.observers.frame_meter.FrameMeterObserver import FrameMeterObserver
from move_parser_by_replay.util.CSVHelper import CSVHelper
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


def test_basic_frame_meter_observer():
    video = Video('./data/match1.mkv')

    frame_meter_observer = FrameMeterObserver(video)
    frame_meter_observer.set_maximum_frame_to_look_at(2000)
    frame_meter_observer.analyse_full_video()

    final_frame_meter_list: List[FrameMeterColumn] = frame_meter_observer.get_final_list_for_states()

    final_list_without_frame_meter_info = []
    for column in final_frame_meter_list:
        final_list_without_frame_meter_info.append(
            FrameMeterColumn(0, column.get_state_by_player(Player.FIRST_PLAYER),
                             column.get_state_by_player(Player.SECOND_PLAYER)))

    expected_frame_meter_list = CSVHelper.read_frame_meter_from_csv('./data/frame_meter.csv')
    p1_list_by_frame = frame_meter_observer.get_exact_list_for_player_as_frame_count(Player.FIRST_PLAYER)
    p2_list_by_frame = frame_meter_observer.get_exact_list_for_player_as_frame_count(Player.SECOND_PLAYER)
    min_length = min(len(final_frame_meter_list), len(expected_frame_meter_list))
    differences = [column.get_differences_with_other(final_frame_meter_list[idx]) for idx, column in
                   enumerate(expected_frame_meter_list[:min_length])]
    ratio_difference = DiffLibWrapper.get_similarity_ratio_from_two_lists(expected_frame_meter_list[:min_length],
                                                                          final_list_without_frame_meter_info[
                                                                          :min_length])
    assert len(final_frame_meter_list) > 0
    assert ratio_difference > 0.5
