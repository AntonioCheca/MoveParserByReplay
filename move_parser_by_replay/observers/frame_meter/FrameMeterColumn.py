from typing import Optional

from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterColumn:
    state: Optional[StateFrameMeterEnum]

    def __init__(self, state: Optional[StateFrameMeterEnum]):
        self.state = state

    def is_past(self) -> bool:
        return self.state is not None and self.state.is_from_the_past()

    def is_unknown_or_nothing(self) -> bool:
        return self.state is None or self.state == StateFrameMeterEnum.NOTHING
