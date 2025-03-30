from typing import Tuple


class Position:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def get_inverted_tuple(self) -> Tuple[int, int]:
        return self.y, self.x