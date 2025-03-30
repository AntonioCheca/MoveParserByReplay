from typing import List

from easyocr import Reader

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface
from move_parser_by_replay.util.number_recognisers.RecognisedNumberInPosition import RecognisedNumberInPosition


class EasyOCRNumberRecogniser(NumberRecogniserInterface):
    reader: Reader

    def __init__(self):
        self.reader = Reader(['en'])

    def get_numbers_in_region(self, region: Frame) -> List[RecognisedNumberInPosition]:
        result_matches = self.reader.readtext(region.get_image_data(), detail=1, allowlist='0123456789')

        recognised_numbers = []
        for match in result_matches:
            position_detected = match[0][0]
            number_detected = int(match[1])
            position = Position(position_detected[0], position_detected[1])
            recognised_number = RecognisedNumberInPosition(position, number_detected)
            recognised_numbers.append(recognised_number)

        return recognised_numbers
