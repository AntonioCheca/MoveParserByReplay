from typing import Optional, Self

from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterColumn:
    p1_state: Optional[StateFrameMeterEnum]
    p2_state: Optional[StateFrameMeterEnum]

    def __init__(self, p1_state: Optional[StateFrameMeterEnum], p2_state: Optional[StateFrameMeterEnum]):
        self.p1_state = p1_state
        self.p2_state = p2_state

    def is_past(self) -> bool:
        is_p1_from_past = self.is_specific_state_from_past(self.p1_state)
        is_p2_from_past = self.is_specific_state_from_past(self.p2_state)
        if not is_p1_from_past and not is_p2_from_past:
            return False

        if is_p1_from_past:
            return is_p2_from_past or self.is_specific_state_unknown_or_nothing(self.p2_state)

        return self.is_specific_state_unknown_or_nothing(self.p1_state)

    def is_unknown_or_nothing(self) -> bool:
        return self.is_specific_state_unknown_or_nothing(self.p1_state) and \
            self.is_specific_state_unknown_or_nothing(self.p2_state)

    @staticmethod
    def is_specific_state_from_past(state: Optional[StateFrameMeterEnum]) -> bool:
        return state is not None and state.is_from_the_past()

    @staticmethod
    def is_specific_state_unknown_or_nothing(state: Optional[StateFrameMeterEnum]) -> bool:
        return state is None or state == StateFrameMeterEnum.NOTHING

    def __hash__(self):
        return hash((self.p1_state, self.p2_state))

    def __eq__(self, other: Self) -> bool:
        return self.p1_state == other.p1_state and self.p2_state == other.p2_state
