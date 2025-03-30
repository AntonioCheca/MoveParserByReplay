import os
from typing import List, Dict, Optional

from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.templates.Button import Button
from move_parser_by_replay.base.templates.Direction import Direction
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.observers.input_display.InputDisplayRow import InputDisplayRow
from move_parser_by_replay.util.NumberInReplayWrapper import NumberInReplayWrapper
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper
from move_parser_by_replay.util.TesseractWrapper import TesseractWrapper


class InputDisplayObserver:
    TEMPLATES_FOR_INPUTS = './data/input_display/'
    TEMPLATES_FOR_NUMBERS = './data/numbers/'
    ROWS_IN_TOTAL_REGION = 4
    NUMBER_FRAME_WIDTH = 50
    region: Region
    player_number: int
    directions: Dict[str, Direction]
    buttons: Dict[str, Button]
    numbers: Dict[str, Number]
    exact_input_row_for_frames: Dict[int, InputDisplayRow]

    def __init__(self, player_number: int, region: Region):
        self.player_number = player_number
        self.region = region
        self.initialise_buttons()
        self.initialise_directions()
        self.initialise_numbers()
        self.exact_input_row_for_frames = {}

    def initialise_directions(self) -> None:
        self.directions = {}
        self.load_templates_from_folder("Direction")

    def initialise_buttons(self) -> None:
        self.buttons = {}
        self.load_templates_from_folder("Button")

    def initialise_numbers(self) -> None:
        self.numbers = {}
        self.load_templates_from_folder("Number", self.TEMPLATES_FOR_NUMBERS)

    def load_templates_from_folder(self, item_type: str, folder: str = TEMPLATES_FOR_INPUTS) -> None:
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Templates directory not found: {folder}")

        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            base_name = os.path.splitext(file_name)[0]

            if os.path.isfile(file_path):
                if item_type == "Direction" and "Direction" in file_name:
                    self.directions[base_name] = Direction(file_path)
                elif item_type == "Button" and "Direction" not in file_name:
                    self.buttons[base_name] = Button(file_path)
                elif item_type == "Number":
                    self.numbers[base_name] = Number(file_path)

    def get_buttons(self) -> Dict[str, Button]:
        return self.buttons

    def get_directions(self) -> Dict[str, Direction]:
        return self.directions

    def get_numbers(self) -> Dict[str, Number]:
        return self.numbers

    def get_exact_input_rows_for_frames(self) -> Dict[int, InputDisplayRow]:
        return self.exact_input_row_for_frames

    def fill_from_video(self, video: Video) -> None:
        for frame in video.get_frames_as_iterator():
            subregion = frame.get_subregion(self.region)
            frame_number = subregion.get_frame_number()

            input_display_row = self.get_input_display_row_from_region(subregion)
            self.exact_input_row_for_frames[frame_number] = input_display_row

    def get_input_display_row_from_region(self, subregion: Frame) -> InputDisplayRow:
        top_row_frame = self.get_top_frame(subregion)

        detected_direction = self.detect_direction_in_input_display(top_row_frame)
        detected_buttons = self.detect_buttons_in_input_display(top_row_frame)

        number_frame = self.get_specific_number_region(top_row_frame)
        detect_pressed_frames = self.detect_pressed_frames_in_input_display(number_frame)

        return InputDisplayRow(detected_direction, detected_buttons, detect_pressed_frames)

    def get_specific_number_region(self, subregion: Frame) -> Frame:
        number_region_height = subregion.height
        number_region = Region(0, 0, self.NUMBER_FRAME_WIDTH, number_region_height)
        number_region_frame = subregion.get_subregion(number_region)
        return number_region_frame

    def detect_pressed_frames_in_input_display(self, top_row_frame: Frame) -> Optional[int]:
        left_digit_frame = top_row_frame.get_left_region()
        right_digit_frame = top_row_frame.get_right_region()

        left_digit_detected = TesseractWrapper.search_numbers_in_image(left_digit_frame)
        right_digit_detected = TesseractWrapper.search_numbers_in_image(right_digit_frame)

        result = 0

        if len(left_digit_detected) == 1:
            result = left_digit_detected[0] * 10
        elif len(left_digit_detected) > 1:
            raise Exception(f'Left digit region detected {len(left_digit_detected)} numbers, expected 0 or 1')

        if len(right_digit_detected) == 1:
            result += right_digit_detected[0]
        elif len(right_digit_detected) > 1:
            raise Exception(f'Right digit region detected {len(right_digit_detected)} numbers, expected 0 or 1')

        if len(left_digit_detected) == 0 and len(right_digit_detected) == 0:
            return None

        return result

    def detect_buttons_in_input_display(self, top_row_frame) -> List[Button]:
        detected_buttons = []
        for button_key in self.buttons:
            button = self.buttons[button_key]
            matches = OpenCVWrapper.search_image_by_template(
                top_row_frame.get_image_data(),
                button.get_image()
            )

            if matches and len(matches) > 0:
                detected_buttons.append(button)
        return detected_buttons

    def detect_direction_in_input_display(self, top_row_frame) -> Optional[Direction]:
        detected_direction = None
        for direction_key in self.directions:
            direction = self.directions[direction_key]
            matches = OpenCVWrapper.search_image_by_template(
                top_row_frame.get_image_data(),
                direction.get_image()
            )

            if matches and len(matches) > 0:
                if detected_direction is not None:
                    raise Exception('We have found TWO directions in InputDisplay, aborting')
                detected_direction = direction

        return detected_direction

    def get_top_frame(self, subregion: Frame) -> Frame:
        top_row_height = subregion.height // self.ROWS_IN_TOTAL_REGION
        top_row_region = Region(0, 0, subregion.width, top_row_height)
        top_row_frame = subregion.get_subregion(top_row_region)
        return top_row_frame
