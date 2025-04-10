from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from typing import Dict, Optional, Tuple

from move_parser_by_replay.observers.frame_meter.StateType import StateType
from move_parser_by_replay.observers.frame_meter.TemporalState import TemporalState


class StateFrameMeterRegistry:
    INSTANCES: Dict[Tuple[StateType, TemporalState], Tuple[StateFrameMeter, int]] = {}

    PRIORITIES: Dict[StateType, int] = {
        StateType.ACTIVE: 1,
        StateType.STARTUP: 1,
        StateType.RECOVERY: 1,
        StateType.HIT_STUCK: 1,
        StateType.JUMP_OR_DASH: 1,
        StateType.ARMOR_PARRY: 1,
        StateType.NOTHING: 3,
        StateType.STRIKE_INVULNERABILITY_1: 5,
        StateType.STRIKE_INVULNERABILITY_2: 5,
        StateType.FULL_INVULNERABILITY_1: 7,
        StateType.FULL_INVULNERABILITY_2: 7,
        StateType.NUMBER_OF_FRAMES_1: 9,
        StateType.NUMBER_OF_FRAMES_2: 9,
        StateType.FRAME_METER_END_OF_FULL_WINDOW: 11
    }

    @classmethod
    def initialize(cls):
        for state_type in StateType:
            for temporal_state in TemporalState:
                state = StateFrameMeter(state_type, temporal_state)
                priority = cls.PRIORITIES[state_type]
                if temporal_state == TemporalState.PAST:
                    priority += 1
                cls.INSTANCES[(state_type, temporal_state)] = (state, priority)

    @classmethod
    def get(cls, state_type: StateType, temporal_state: TemporalState) -> StateFrameMeter:
        return cls.INSTANCES[(state_type, temporal_state)][0]

    @classmethod
    def get_priority(cls, state_type: StateType, temporal_state: TemporalState) -> int:
        return cls.INSTANCES[(state_type, temporal_state)][1]

    @classmethod
    def from_csv_value(cls, csv_value: str) -> Optional[StateFrameMeter]:
        mapping = {
            'STARTUP': StateType.STARTUP,
            'ACTIVE': StateType.ACTIVE,
            'RECOVERY': StateType.RECOVERY,
            'HITSTUCK': StateType.HIT_STUCK,
            'NOTHING': StateType.NOTHING,
            'JUMP': StateType.JUMP_OR_DASH,
            'PARRY': StateType.ARMOR_PARRY,
            'FULL INVULNERABILITY': StateType.FULL_INVULNERABILITY_1,
            'STRIKE INVULNERABILITY': StateType.STRIKE_INVULNERABILITY_1
        }

        state_type = mapping.get(csv_value)
        if state_type:
            return cls.get(state_type, TemporalState.PRESENT)
        return None


# Initialize the registry
StateFrameMeterRegistry.initialize()
