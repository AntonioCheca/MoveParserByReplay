from typing import Tuple, Self, Dict, Optional
import numpy as np

from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from move_parser_by_replay.observers.frame_meter.StateFrameMeterRegistry import StateFrameMeterRegistry
from move_parser_by_replay.observers.frame_meter.StateType import StateType
from move_parser_by_replay.observers.frame_meter.TemporalState import TemporalState


class ColorFrameMeter:
    ALL_COLORS: Dict[StateFrameMeter, Tuple[int, int, int]] = {
        StateFrameMeterRegistry.get(StateType.ACTIVE, TemporalState.PRESENT): (99, 21, 189),
        StateFrameMeterRegistry.get(StateType.STARTUP, TemporalState.PRESENT): (148, 203, 12),
        StateFrameMeterRegistry.get(StateType.RECOVERY, TemporalState.PRESENT): (184, 119, 9),
        StateFrameMeterRegistry.get(StateType.FULL_INVULNERABILITY_1, TemporalState.PRESENT): (244, 241, 242),
        StateFrameMeterRegistry.get(StateType.FULL_INVULNERABILITY_2, TemporalState.PRESENT): (197, 194, 195),
        StateFrameMeterRegistry.get(StateType.HIT_STUCK, TemporalState.PRESENT): (55, 255, 252),
        # StateFrameMeter.NUMBER_OF_FRAMES_1: (33, 32, 19),
        StateFrameMeterRegistry.get(StateType.NUMBER_OF_FRAMES_2, TemporalState.PRESENT): (105, 82, 41),
        StateFrameMeterRegistry.get(StateType.RECOVERY, TemporalState.PAST): (134, 86, 5),
        StateFrameMeterRegistry.get(StateType.ACTIVE, TemporalState.PAST): (73, 12, 136),
        StateFrameMeterRegistry.get(StateType.STARTUP, TemporalState.PAST): (108, 146, 11),
        StateFrameMeterRegistry.get(StateType.JUMP_OR_DASH, TemporalState.PAST): (183, 195, 57),
        StateFrameMeterRegistry.get(StateType.HIT_STUCK, TemporalState.PAST): (37, 192, 185),
        StateFrameMeterRegistry.get(StateType.FULL_INVULNERABILITY_1, TemporalState.PAST): (176, 176, 176),
        StateFrameMeterRegistry.get(StateType.FULL_INVULNERABILITY_2, TemporalState.PAST): (144, 144, 144),
        StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PRESENT): (27, 24, 25),
        StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PAST): (16, 16, 16),
        StateFrameMeterRegistry.get(StateType.JUMP_OR_DASH, TemporalState.PRESENT): (249, 255, 82),
        StateFrameMeterRegistry.get(StateType.ARMOR_PARRY, TemporalState.PRESENT): (106, 16, 86),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1: (92, 23, 185),
        StateFrameMeterRegistry.get(StateType.STRIKE_INVULNERABILITY_2, TemporalState.PRESENT): (251, 209, 255),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1: (63, 10, 137),
        StateFrameMeterRegistry.get(StateType.STRIKE_INVULNERABILITY_2, TemporalState.PAST): (184, 155, 212),
        StateFrameMeterRegistry.get(StateType.ARMOR_PARRY, TemporalState.PAST): (76, 8, 60),
    }

    THRESHOLD_FOR_DISTANCE = 200

    _color_cache: Dict[Tuple[int, int, int], Optional[StateFrameMeter]] = {}
    _states_array = None
    _colors_array = None
    _initialized = False

    color: Tuple[int, int, int]

    def __init__(self, color: Tuple[int, int, int]):
        self.color = color
        if not ColorFrameMeter._initialized:
            self._initialize_color_arrays_in_numpy()

    @classmethod
    def _initialize_color_arrays_in_numpy(cls):
        cls._states_array = list(cls.ALL_COLORS.keys())
        cls._colors_array = np.array(list(cls.ALL_COLORS.values()))
        cls._initialized = True

    def get_potential_state_frame_meter(self) -> Optional[StateFrameMeter]:
        color_key = self.color
        if color_key in self._color_cache:
            return self._color_cache[color_key]

        color_array = np.array(self.color)
        diff = self._colors_array - color_array
        distances = np.sum(diff * diff, axis=1)

        min_idx = np.argmin(distances)
        min_distance = distances[min_idx]

        if min_distance <= self.THRESHOLD_FOR_DISTANCE:
            result = self._states_array[min_idx]
        else:
            result = None

        self._color_cache[color_key] = result
        return result

    def distance_with_another_color(self, other: Self) -> int:
        b_diff = self.color[0] - other.color[0]
        g_diff = self.color[1] - other.color[1]
        r_diff = self.color[2] - other.color[2]

        return b_diff * b_diff + g_diff * g_diff + r_diff * r_diff

    def distance_with_tuple_color(self, color_as_tuple: Tuple[int, int, int]) -> int:
        b_diff = self.color[0] - color_as_tuple[0]
        g_diff = self.color[1] - color_as_tuple[1]
        r_diff = self.color[2] - color_as_tuple[2]

        return b_diff * b_diff + g_diff * g_diff + r_diff * r_diff
