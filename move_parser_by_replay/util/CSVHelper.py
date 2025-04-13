import csv
from typing import List, Optional

from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from move_parser_by_replay.observers.frame_meter.StateFrameMeterRegistry import StateFrameMeterRegistry
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow


class CSVHelper:
    FINISH_ROUND_TAG = 'FINISH_ROUND'

    @classmethod
    def read_input_display_from_csv(cls, csv_path: str, input_display_observer: InputDisplayTemplateObserver) -> List[
        InputDisplayRow]:
        rows = []

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                all_buttons_raw = row['Buttons']
                if all_buttons_raw != cls.FINISH_ROUND_TAG:
                    direction_name = '{}Direction'.format(row['Directions'])

                    frames = int(row['Frames']) if row['Frames'].isnumeric() else None

                    if all_buttons_raw.strip() == '':
                        input_display_row = InputDisplayRow(input_display_observer.get_directions()[direction_name],
                                                            ListOfButtons([]),
                                                            frames)
                    else:
                        button_names_raw = all_buttons_raw.split(',')
                        button_names = [Button.get_name_from_numpad_notation(button) for button in button_names_raw]
                        list_of_buttons = ListOfButtons([])
                        for button_name in button_names:
                            list_of_buttons.append(input_display_observer.get_buttons()[button_name])

                        input_display_row = InputDisplayRow(input_display_observer.get_directions()[direction_name],
                                                            list_of_buttons,
                                                            frames)

                    rows.append(input_display_row)

        return rows

    @classmethod
    def read_frame_meter_from_csv(cls, csv_path: str) -> List[FrameMeterColumn]:
        columns = []
        p1_states = []
        p2_states = []

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                p1_state = StateFrameMeterRegistry.from_csv_value(row['P1-State'])
                p2_state = StateFrameMeterRegistry.from_csv_value(row['P2-State'])
                if p1_state is not None:
                    p1_frames = int(row['P1-Number'])
                    p1_states.append((p1_state, p1_frames))
                if p2_state is not None:
                    p2_frames = int(row['P2-Number'])
                    p2_states.append((p2_state, p2_frames))

        p1_index = 0
        p2_index = 0
        p1_frames_used = 0
        p2_frames_used = 0

        while p1_index < len(p1_states) or p2_index < len(p2_states):
            p1_state: Optional[StateFrameMeter] = None
            p2_state: Optional[StateFrameMeter] = None

            if p1_index < len(p1_states):
                current_p1_state, total_p1_frames = p1_states[p1_index]
                p1_state = current_p1_state
                p1_frames_used += 1

                if p1_frames_used >= total_p1_frames:
                    p1_index += 1
                    p1_frames_used = 0

            if p2_index < len(p2_states):
                current_p2_state, total_p2_frames = p2_states[p2_index]
                p2_state = current_p2_state
                p2_frames_used += 1

                if p2_frames_used >= total_p2_frames:
                    p2_index += 1
                    p2_frames_used = 0

            columns.append(FrameMeterColumn(0, p1_state, p2_state))

        return columns
