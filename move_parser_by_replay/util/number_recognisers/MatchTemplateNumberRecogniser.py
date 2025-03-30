from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.templates.Number import Number
from move_parser_by_replay.util.NumberInReplayWrapper import NumberInReplayWrapper
from move_parser_by_replay.util.number_recognisers.NumberRecogniserInterface import NumberRecogniserInterface
from move_parser_by_replay.util.number_recognisers.RecognisedNumberInPosition import RecognisedNumberInPosition


class MatchTemplateNumberRecogniser(NumberRecogniserInterface):
    BOTTOM_Y_FOR_SUBREGION = 228
    HEIGHT_Y_FOR_SUBREGION = 645
    numbers: Dict[str, Number]

    def __init__(self, numbers: Dict[str, Number]):
        self.numbers = numbers

    def get_numbers_in_region(self, region: Frame) -> List[RecognisedNumberInPosition]:
        matches = NumberInReplayWrapper.search_numbers_in_image(region, self.numbers)

        recognised_numbers = []
        for match in matches:
            recognised_number = match[0]
            recognised_position = match[1]
            position = Position(recognised_position[0], recognised_position[1])
            recognised_numbers.append(RecognisedNumberInPosition(position, recognised_number))

        return recognised_numbers

    @classmethod
    def get_subregion(cls, frame: Frame, player: Player) -> Frame:
        if player == Player.FIRST_PLAYER:
            region = Region(54, cls.BOTTOM_Y_FOR_SUBREGION, 26, cls.HEIGHT_Y_FOR_SUBREGION)
        else:
            region = Region(1920 - 54 - 26, cls.BOTTOM_Y_FOR_SUBREGION, 26, cls.HEIGHT_Y_FOR_SUBREGION)

        return frame.get_subregion(region)
