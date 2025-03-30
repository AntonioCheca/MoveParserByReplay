from typing import List

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.util.TesseractWrapper import TesseractWrapper
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface
from move_parser_by_replay.util.number_recognisers.RecognisedNumberInPosition import RecognisedNumberInPosition


class TesseractNumberRecogniser(NumberRecogniserInterface):
    def get_numbers_in_region(self, region: Frame) -> List[RecognisedNumberInPosition]:
        text = TesseractWrapper.search_text_in_image(region)

        return []
