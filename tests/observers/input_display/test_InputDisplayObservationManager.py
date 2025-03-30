from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayObserver


def test_apply_base_observations():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayObserver(video)
    manager = input_display_observer.get_manager()

    manager.set_window_to_stop_searching(8000)
    manager.apply_base_observations_in_window(0, video.get_frame_count() - 1)
    observations = manager.get_observations()

    count_not_none = 0
    for frame_key in observations:
        if observations[frame_key] is not None:
            count_not_none += 1

    assert count_not_none > 0
    assert count_not_none <= video.get_frame_count()
