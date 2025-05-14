from typing import Dict, Optional

from move_parser_by_replay.base.framedata.Move import Move
from move_parser_by_replay.base.framedata.MoveType import MoveType


class Character:
    def __init__(self, name: str):
        self.name = name
        self.moves: Dict[str, Move] = {}

    def get_name(self) -> str:
        return self.name

    def add_move(self, move: Move) -> None:
        self.moves[move.get_move_name()] = move

    def get_move(self, move_name: str) -> Optional[Move]:
        return self.moves.get(move_name)

    def get_moves(self) -> Dict[str, Move]:
        return self.moves

    def get_moves_by_type(self, move_type: MoveType) -> Dict[str, Move]:
        return {name: move for name, move in self.moves.items()
                if move.get_move_type() == move_type}

    def __str__(self) -> str:
        return self.name
