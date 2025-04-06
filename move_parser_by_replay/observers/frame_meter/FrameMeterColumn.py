from typing import Optional, Self, List

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class FrameMeterColumn:
    p1_state: Optional[StateFrameMeterEnum]
    p2_state: Optional[StateFrameMeterEnum]
    column_position: int
    frame_meter_in_match: int

    def __init__(self, p1_state: Optional[StateFrameMeterEnum], p2_state: Optional[StateFrameMeterEnum],
                 column_position: int, frame_meter_in_match):
        self.p1_state = p1_state
        self.p2_state = p2_state
        self.column_position = column_position
        self.frame_meter_in_match = frame_meter_in_match

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

    def is_end_of_window(self) -> bool:
        return self.p1_state is not None and self.p2_state is not None and \
            self.p1_state == StateFrameMeterEnum.FRAME_METER_END_OF_FULL_WINDOW and \
            self.p2_state == StateFrameMeterEnum.FRAME_METER_END_OF_FULL_WINDOW

    def get_state_for_player(self, player: Player) -> Optional[StateFrameMeterEnum]:
        if player == Player.FIRST_PLAYER:
            return self.p1_state
        return self.p2_state

    def get_column_position(self) -> int:
        return self.column_position

    def get_frame_meter_in_match(self) -> int:
        return self.frame_meter_in_match

    def reduce_frame_meter_in_match(self) -> None:
        self.frame_meter_in_match -= 1

    def set_state_for_player(self, player: Player, state: Optional[StateFrameMeterEnum]) -> None:
        if player == Player.FIRST_PLAYER:
            self.p1_state = state
        else:
            self.p2_state = state

    def transform_from_past_to_present(self) -> Self:
        new_p1_state = self.p1_state if self.p1_state is None else self.p1_state.transform_from_past_to_present()
        new_p2_state = self.p2_state if self.p2_state is None else self.p2_state.transform_from_past_to_present()
        return FrameMeterColumn(new_p1_state, new_p2_state, self.column_position, self.frame_meter_in_match)

    @staticmethod
    def is_specific_state_from_past(state: Optional[StateFrameMeterEnum]) -> bool:
        return state is not None and state.is_from_the_past()

    @staticmethod
    def is_specific_state_unknown_or_nothing(state: Optional[StateFrameMeterEnum]) -> bool:
        return state is None or state in [StateFrameMeterEnum.NOTHING, StateFrameMeterEnum.NOTHING_PAST]

    @classmethod
    def get_end_window_column(cls, frame_meter_in_match: int):
        return cls(StateFrameMeterEnum.FRAME_METER_END_OF_FULL_WINDOW,
                   StateFrameMeterEnum.FRAME_METER_END_OF_FULL_WINDOW, 81, frame_meter_in_match)

    def __hash__(self):
        return hash((self.p1_state, self.p2_state, self.column_position, self.frame_meter_in_match))

    def __eq__(self, other: Self) -> bool:
        return self.p1_state == other.p1_state and self.p2_state == other.p2_state and \
            self.column_position == other.column_position and self.frame_meter_in_match == other.frame_meter_in_match

    def __repr__(self) -> str:
        return "P1 state {}, P2 state {}, column {}, frame meter {}".format(str(self.p1_state), str(self.p2_state),
                                                                            str(self.column_position),
                                                                            str(self.frame_meter_in_match))

    def get_differences_with_other(self, other: Self) -> List[str]:
        differences = []

        if self.p1_state != other.p1_state:
            differences.append('P1 State, {} vs {}'.format(str(self.p1_state), str(other.p1_state)))
        if self.p2_state != other.p2_state:
            differences.append('P2 State, {} vs {}'.format(str(self.p2_state), str(other.p2_state)))

        return differences
