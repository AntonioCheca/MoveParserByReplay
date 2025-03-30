from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayObserver
from move_parser_by_replay.base.Region import Region


def test_constructor_loads_templates_properly():
    margin = 42
    input_display_width = 290
    input_display_height = 143
    input_display_altitude = 225
    input_display = InputDisplayObserver(1,
                                         Region(margin, input_display_altitude, input_display_width,
                                                input_display_height))
    assert 9 == len(input_display.get_directions())
    assert 6 == len(input_display.get_buttons())


def test_only_specific_frame_for_input_display():
    margin = 42
    input_display_width = 290
    input_display_height = 143
    input_display_altitude = 225
    input_display = InputDisplayObserver(1,
                                         Region(margin, input_display_altitude, input_display_width,
                                                input_display_height))

    video = Video('./data/match1.mkv')
    input_display.fill_from_video(video)

    dict_of_input_display_rows = input_display.get_exact_input_rows_for_frames()
    assert 0 == len(dict_of_input_display_rows)
    assert 250 == dict_of_input_display_rows[250].get_frame_number()
    assert [] == dict_of_input_display_rows[250].get_buttons()
    assert input_display.get_directions()['NeutralDirection'] == dict_of_input_display_rows[250].get_direction()
