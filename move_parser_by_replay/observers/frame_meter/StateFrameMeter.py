from typing import Optional, Self

from move_parser_by_replay.observers.frame_meter.StateType import StateType
from move_parser_by_replay.observers.frame_meter.TemporalState import TemporalState


class StateFrameMeter:
    state_type: StateType
    temporal_state: TemporalState

    def __init__(self, state_type: StateType, temporal_state: TemporalState):
        self.state_type = state_type
        self.temporal_state = temporal_state

    def get_state_type(self) -> StateType:
        return self.state_type

    def get_temporal_state(self) -> TemporalState:
        return self.temporal_state

    def get_description(self) -> str:
        base_value = self.state_type.value
        if self.temporal_state == TemporalState.PAST:
            return f"{base_value} (Past)"
        return base_value

    def is_from_the_past(self) -> bool:
        return self.temporal_state == TemporalState.PAST

    def is_from_the_present(self) -> bool:
        return self.temporal_state == TemporalState.PRESENT

    def is_nothing(self) -> bool:
        return self.state_type == StateType.NOTHING

    def cannot_be_followed_by_none(self) -> bool:
        return self.state_type in [StateType.ACTIVE, StateType.STARTUP]

    def to_present(self) -> Optional[Self]:
        if self.temporal_state == TemporalState.PRESENT:
            return None
        return StateFrameMeter(self.state_type, TemporalState.PRESENT)

    def to_past(self) -> Optional[Self]:
        if self.temporal_state == TemporalState.PAST:
            return None
        return StateFrameMeter(self.state_type, TemporalState.PAST)

    def is_it_possible_in_final_list(self) -> bool:
        if self.temporal_state == TemporalState.PAST:
            return False
        if self.state_type in [StateType.NUMBER_OF_FRAMES_1, StateType.NUMBER_OF_FRAMES_2]:
            return False
        if self.state_type == StateType.FRAME_METER_END_OF_FULL_WINDOW:
            return False
        return True

    def __eq__(self, other: Self) -> bool:
        if other is None:
            return False

        return self.state_type == other.state_type and self.temporal_state == other.temporal_state

    def __hash__(self) -> int:
        return hash((self.state_type, self.temporal_state))

    def __repr__(self) -> str:
        return self.get_description()

    def __str__(self) -> str:
        return self.get_description()
