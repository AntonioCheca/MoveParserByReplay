from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.util.CSVInputDisplayRowHelper import CSVInputDisplayRowHelper


def test_csv_reader():
    video = Video('./data/match1.mkv')
    input_display_observer = InputDisplayTemplateObserver(video)

    list_of_expected_input_displays = CSVInputDisplayRowHelper.read_from_csv('./data/match1-inputdisplay.csv',
                                                                             input_display_observer)

    assert len(list_of_expected_input_displays) > 0
