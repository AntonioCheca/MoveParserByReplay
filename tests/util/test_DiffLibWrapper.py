from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.input_display.InputDisplayObservationRow import InputDisplayObservationRow
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayObserver
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


def get_example_input_display_observation_row() -> InputDisplayObservationRow:
    observer = InputDisplayObserver(Video('./data/match1.mkv'))

    input_display_row = InputDisplayObservationRow()
    input_display_row.add_frames_pressed_observation(56, 99)
    input_display_row.add_direction_pressed_observation(observer.get_directions()['NeutralDirection'])

    list_of_buttons_pressed = [observer.get_buttons()['HeavyPunch'], observer.get_buttons()['LightKick']]
    input_display_row.add_buttons_pressed_observation(ListOfButtons(list_of_buttons_pressed))

    return input_display_row


def test_ratio_is_1_when_comparing_same_lists():
    first_list = []
    first_list.append(get_example_input_display_observation_row())
    second_list = []
    second_list.append(get_example_input_display_observation_row())

    hash1 = hash(first_list[0])
    hash2 = hash(second_list[0])
    eq1 = first_list[0] == second_list[0]
    assert 1 == DiffLibWrapper.get_similarity_ratio_from_two_lists(first_list, second_list)
