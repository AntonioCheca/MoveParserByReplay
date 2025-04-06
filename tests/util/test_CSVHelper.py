from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.util.CSVHelper import CSVHelper


def test_csv_reader():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayTemplateObserver(video)

    list_of_expected_input_displays = CSVHelper.read_input_display_from_csv('./data/match1-inputdisplay.csv',
                                                                            input_display_observer)

    assert len(list_of_expected_input_displays) > 0


def test_csv_reader_frame_meter():
    list_of_expected_frame_meter = CSVHelper.read_frame_meter_from_csv('./data/frame_meter.csv')

    assert len(list_of_expected_frame_meter) == 1667
