from move_parser_by_replay.base.Position import Position


class RecognisedNumberInPosition:
    position: Position
    number: int

    def __init__(self, position: Position, number: int):
        self.position = position
        self.number = number

    def get_position(self) -> Position:
        return self.position

    def get_number(self) -> int:
        return self.number
