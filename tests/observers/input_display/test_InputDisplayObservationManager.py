from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayObserver
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.observers.input_display.MergerForInputDisplayObservations import \
    MergerForInputDisplayObservations
from move_parser_by_replay.util.CSVInputDisplayRowHelper import CSVInputDisplayRowHelper
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


def test_apply_base_observations():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    manager.set_window_to_stop_searching(8000)
    manager.analyse_full_video()
    observations = manager.get_observations()

    count_not_none = 0
    for frame_key in observations:
        if observations[frame_key] is not None:
            count_not_none += 1

    assert count_not_none > 0
    assert count_not_none <= video.get_frame_count()


def test_merger_basic_construction():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    first_frame = 1000
    second_frame = first_frame + 30
    first_observation = manager.apply_observations_in_frame(first_frame)
    second_observation = manager.apply_observations_in_frame(second_frame)

    merged_inputs = MergerForInputDisplayObservations.merge_input_displays(first_observation, first_frame,
                                                                           second_observation,
                                                                           second_frame, Player.FIRST_PLAYER)

    assert merged_inputs is not None
    assert 0 < len(merged_inputs)


def test_merger_returns_none_when_there_is_no_overlap():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    first_frame = 1000
    second_frame = first_frame + 500
    first_observation = manager.apply_observations_in_frame(first_frame)
    second_observation = manager.apply_observations_in_frame(second_frame)

    merged_inputs = MergerForInputDisplayObservations.merge_input_displays(first_observation, first_frame,
                                                                           second_observation,
                                                                           second_frame, Player.FIRST_PLAYER)

    assert merged_inputs is None


def test_analyse_full_video_always_has_three_frames_if_window_is_too_high():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    manager.set_window_to_stop_searching(100000)
    manager.analyse_full_video()
    observations = manager.get_observations()

    count_not_none = 0
    for frame_key in observations:
        if observations[frame_key] is not None:
            count_not_none += 1

    assert 3 == count_not_none


def test_analyse_full_video_creates_merged_input_display_rows():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    manager.set_window_to_stop_searching(45)
    manager.set_maximum_frame_to_look_at(2000)
    manager.analyse_full_video()

    assert len(manager.merged_display_rows) > 0

    list_of_expected_input_displays = CSVInputDisplayRowHelper.read_from_csv('./data/match1-inputdisplay.csv',
                                                                             input_display_observer)[
                                      :len(manager.merged_display_rows)]
    differences = [row.get_differences_with_other_input_display_row(manager.merged_display_rows[idx]) for idx, row in
                   enumerate(list_of_expected_input_displays)]

    assert DiffLibWrapper.get_similarity_ratio_from_two_lists(list_of_expected_input_displays,
                                                              manager.merged_display_rows) > 0.5
