import csv
from typing import List

from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.ListOfButtons import ListOfButtons
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow


class CSVInputDisplayRowHelper:
    FINISH_ROUND_TAG = 'FINISH_ROUND'

    @classmethod
    def read_from_csv(cls, csv_path: str, input_display_observer: InputDisplayTemplateObserver) -> List[
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
