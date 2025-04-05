from typing import Optional, Self

from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterColumn:
    p1_state: Optional[StateFrameMeterEnum]
    p2_state: Optional[StateFrameMeterEnum]

    def __init__(self, p1_state: Optional[StateFrameMeterEnum], p2_state: Optional[StateFrameMeterEnum]):
        self.p1_state = p1_state
        self.p2_state = p2_state

    def is_past(self) -> bool:
        return self.p1_state is not None and self.p1_state.is_from_the_past() and \
            self.p2_state is not None and self.p2_state.is_from_the_past()

    def is_unknown_or_nothing(self) -> bool:
        return (self.p1_state is None or self.p1_state == StateFrameMeterEnum.NOTHING) and (
                self.p2_state is None or self.p2_state == StateFrameMeterEnum.NOTHING)

    def __hash__(self):
        return hash((self.p1_state, self.p2_state))

    def __eq__(self, other: Self) -> bool:
        return self.p1_state == other.p1_state and self.p2_state == other.p2_state
