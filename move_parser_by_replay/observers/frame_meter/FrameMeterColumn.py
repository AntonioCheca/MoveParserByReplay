from typing import Self, List

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter


class FrameMeterColumn:
    p1_state: StateFrameMeter
    p2_state: StateFrameMeter
    column_position: int

    def __init__(self, column_position: int, p1_state: StateFrameMeter, p2_state: StateFrameMeter):
        self.p1_state = p1_state
        self.p2_state = p2_state
        self.column_position = column_position

    def get_state_by_player(self, player: Player) -> StateFrameMeter:
        if player == Player.FIRST_PLAYER:
            return self.p1_state
        else:
            return self.p2_state

    def get_column_position(self) -> int:
        return self.column_position

    def __hash__(self):
        return hash((self.p1_state, self.p2_state, self.column_position))

    def __eq__(self, other: Self) -> bool:
        return self.p1_state == other.p1_state and self.p2_state == other.p2_state and \
            self.column_position == other.column_position

    def __repr__(self) -> str:
        return "P1 state {}, P2 state {}, column {}".format(str(self.p1_state), str(self.p2_state),
                                                            str(self.column_position))

    def get_differences_with_other(self, other: Self) -> List[str]:
        differences = []

        if self.p1_state != other.p1_state:
            differences.append('P1 State, {} vs {}'.format(str(self.p1_state), str(other.p1_state)))

        if self.p2_state != other.p2_state:
            differences.append('P2 State, {} vs {}'.format(str(self.p2_state), str(other.p2_state)))

        return differences
