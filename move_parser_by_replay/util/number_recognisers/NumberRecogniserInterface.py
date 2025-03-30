from abc import ABC, abstractmethod
from typing import List

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.util.number_recognisers.RecognisedNumberInPosition import RecognisedNumberInPosition


class NumberRecogniserInterface(ABC):
    @abstractmethod
    def get_numbers_in_region(self, region: Frame) -> List[RecognisedNumberInPosition]:
        pass
