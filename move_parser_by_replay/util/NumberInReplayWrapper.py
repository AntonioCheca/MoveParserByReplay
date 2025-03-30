from typing import List, Dict
from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class NumberInReplayWrapper:
    @staticmethod
    def search_numbers_in_image(image: Frame, numbers: Dict[str, Number]) -> List[int]:
        image_data = image.get_image_data()
        match_positions = []

        for number_value, number_template in numbers.items():
            template_data = number_template.get_image()
            matches = OpenCVWrapper.search_image_by_template(image_data, template_data)

            for match in matches:
                match_positions.append((match[0], match[1], number_value))

        match_positions.sort(key=lambda pos: (pos[1], pos[0]))

        grouped_numbers = []
        current_group = []
        min_x_threshold = 10
        max_x_threshold = 25
        y_threshold = 2  # Adjust based on row alignment

        for i, (x, y, value) in enumerate(match_positions):
            if not current_group:
                current_group.append((x, value))
                continue

            last_x, last_y, last_value = match_positions[i - 1]

            if abs(y - last_y) <= y_threshold and abs(x - last_x) <= min_x_threshold:
                continue
            elif abs(x - last_x) <= max_x_threshold:
                current_group.append((x, value))
            else:
                grouped_numbers.append("".join(v for _, v in sorted(current_group)))
                current_group = [(x, value)]

        if current_group:
            grouped_numbers.append("".join(v for _, v in sorted(current_group)))

        return [int(num) for num in grouped_numbers]
