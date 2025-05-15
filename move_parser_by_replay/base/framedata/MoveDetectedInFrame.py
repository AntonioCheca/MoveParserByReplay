from move_parser_by_replay.base.framedata.Move import Move
from enum import Enum


class MoveStatus(Enum):
    FULL_ANIMATION = "FULL_ANIMATION"
    PARTIALLY_HIT = "PARTIALLY_HIT"


class MoveDetectedInFrame:
    def __init__(self, start_frame: int, end_frame: int, move: Move, status: MoveStatus):
        self._start_frame = start_frame
        self._end_frame = end_frame
        self._move = move
        self._status = status

    def get_start_frame(self) -> int:
        return self._start_frame

    def get_end_frame(self) -> int:
        return self._end_frame

    def get_move(self) -> Move:
        return self._move

    def get_status(self) -> MoveStatus:
        return self._status

    def __str__(self) -> str:
        return ", ".join([str(item_from_object) for item_from_object in
                          [self._start_frame, self._end_frame, self._move, self._status]])

    def __repr__(self) -> str:
        return str(self)
