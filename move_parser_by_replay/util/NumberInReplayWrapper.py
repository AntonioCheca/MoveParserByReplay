from typing import List, Dict, Tuple
from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class NumberInReplayWrapper:
    @staticmethod
    def search_numbers_in_image(image: Frame, numbers: Dict[str, Number]) -> List[Tuple[int, Tuple[int, int]]]:
        image_data = image.get_image_data()
        match_positions = []

        for number_value, number_template in numbers.items():
            template_data = number_template.get_image()
            matches = OpenCVWrapper.search_image_by_template(image_data, template_data)

            for match in matches:
                match_positions.append((match[0], match[1], number_value))

        # Sort by Y (rows first), then by X (columns within each row)
        match_positions.sort(key=lambda pos: (pos[1], pos[0]))

        grouped_numbers = []
        current_group = []
        min_x_threshold = 10
        max_x_threshold = 25
        y_threshold = 2  # Adjust based on row alignment

        for i, (x, y, value) in enumerate(match_positions):
            if not current_group:
                current_group.append((x, y, value))
                continue

            last_x, last_y, last_value = match_positions[i - 1]

            if abs(y - last_y) <= y_threshold and abs(x - last_x) <= min_x_threshold:
                continue
            elif abs(x - last_x) <= max_x_threshold:
                current_group.append((x, y, value))
            else:
                number_str = "".join(v for _, _, v in sorted(current_group))
                leftmost_x, leftmost_y, _ = min(current_group, key=lambda pos: pos[0])
                grouped_numbers.append((int(number_str), (leftmost_x, leftmost_y)))
                current_group = [(x, y, value)]

        if current_group:
            number_str = "".join(v for _, _, v in sorted(current_group))
            leftmost_x, leftmost_y, _ = min(current_group, key=lambda pos: pos[0])
            grouped_numbers.append((int(number_str), (leftmost_x, leftmost_y)))

        return grouped_numbers
