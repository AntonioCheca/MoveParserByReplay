from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.frame_meter.FrameMeterObserver import FrameMeterObserver


def test_basic_frame_meter_observer():
    video = Video('./data/match1.mkv')

    frame_meter_observer = FrameMeterObserver(video)
    frame_meter_observer.analyse_full_video()

    final_frame_meter_list = frame_meter_observer.get_exact_final_list()

    assert len(final_frame_meter_list) > 0
