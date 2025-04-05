from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.input_display.InputDisplayObservationRow import InputDisplayObservationRow
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


def get_example_input_display_observation_row() -> InputDisplayObservationRow:
    observer = InputDisplayTemplateObserver(Video('./data/match1.mkv'))

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


def test_merge_sequences_on_text_happy_path():
    first_list = ['Hi', 'Hello', 'First overlap', 'Second overlap', 'Third overlap']
    second_list = ['First overlap', 'Second overlap', 'Third overlap', 'Hi', 'Last part']

    expected_output = ['Hi', 'Hello', 'First overlap', 'Second overlap', 'Third overlap', 'Hi', 'Last part']
    assert expected_output == DiffLibWrapper.merge_sequences(first_list, second_list)


def test_merge_sequences_on_text_with_noise_in_overlap():
    first_list = ['Hi', 'Hello', 'First overlap', 'Second overlap', 'Some noise', 'Third overlap', 'Fourth overlap']
    second_list = ['First overlap', 'Second overlap', 'Third overlap', 'Fourth overlap', 'Hi', 'Last part']

    expected_output = ['Hi', 'Hello', 'First overlap', 'Second overlap', 'Some noise', 'Third overlap',
                       'Fourth overlap', 'Hi', 'Last part']
    assert expected_output == DiffLibWrapper.merge_sequences(first_list, second_list)


def test_complex_merge_with_input_display_rows():
    observer = InputDisplayTemplateObserver(Video('./data/match1.mkv'))
    buttons = observer.get_buttons()
    directions = observer.get_directions()

    neutral = directions['NeutralDirection']
    left = directions['LeftDirection']

    first_list = []
    first_list.append(InputDisplayRow(neutral, ListOfButtons([buttons['HeavyPunch']]), 4))
    first_list.append(InputDisplayRow(left, ListOfButtons([]), 90))
    first_list.append(InputDisplayRow(neutral, ListOfButtons([]), None))

    second_list = []
    second_list.append(InputDisplayRow(left, ListOfButtons([]), 90))
    second_list.append(InputDisplayRow(neutral, ListOfButtons([]), None))
    second_list.append(InputDisplayRow(left, ListOfButtons([buttons['HeavyKick']]), None))

    expected_result = []
    expected_result.append(InputDisplayRow(neutral, ListOfButtons([buttons['HeavyPunch']]), 4))
    expected_result.append(InputDisplayRow(left, ListOfButtons([]), 90))
    expected_result.append(InputDisplayRow(neutral, ListOfButtons([]), None))
    expected_result.append(InputDisplayRow(left, ListOfButtons([buttons['HeavyKick']]), None))

    assert expected_result == DiffLibWrapper.merge_sequences(first_list, second_list)
