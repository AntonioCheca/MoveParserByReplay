from typing import Tuple, Self, Dict, Optional
import numpy as np

from move_parser_by_replay.observers.frame_meter.StateFrameMeterEnum import StateFrameMeterEnum


class ColorFrameMeter:
    ALL_COLORS: Dict[StateFrameMeterEnum, Tuple[int, int, int]] = {
        StateFrameMeterEnum.ACTIVE: (99, 21, 189),
        StateFrameMeterEnum.STARTUP: (148, 203, 12),
        StateFrameMeterEnum.RECOVERY: (184, 119, 9),
        StateFrameMeterEnum.FULL_INVULNERABILITY_1: (244, 241, 242),
        StateFrameMeterEnum.FULL_INVULNERABILITY_2: (197, 194, 195),
        StateFrameMeterEnum.HIT_STUCK: (55, 255, 252),
        # StateFrameMeter.NUMBER_OF_FRAMES_1: (33, 32, 19),
        StateFrameMeterEnum.NUMBER_OF_FRAMES_2: (105, 82, 41),
        StateFrameMeterEnum.RECOVERY_PAST: (134, 86, 5),
        StateFrameMeterEnum.ACTIVE_PAST: (73, 12, 136),
        StateFrameMeterEnum.STARTUP_PAST: (108, 146, 11),
        StateFrameMeterEnum.JUMP_OR_DASH_PAST: (183, 195, 57),
        StateFrameMeterEnum.HIT_STUCK_PAST: (37, 192, 185),
        StateFrameMeterEnum.FULL_INVULNERABILITY_1_PAST: (176, 176, 176),
        StateFrameMeterEnum.FULL_INVULNERABILITY_2_PAST: (144, 144, 144),
        StateFrameMeterEnum.NOTHING: (27, 24, 25),
        StateFrameMeterEnum.JUMP_OR_DASH: (249, 255, 82),
        StateFrameMeterEnum.ARMOR_PARRY: (106, 16, 86),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1: (92, 23, 185),
        StateFrameMeterEnum.STRIKE_INVULNERABILITY_2: (251, 209, 255),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1_PAST: (63, 10, 137),
        StateFrameMeterEnum.STRIKE_INVULNERABILITY_2_PAST: (184, 155, 212),
        StateFrameMeterEnum.ARMOR_PARRY_PAST: (76, 8, 60),
    }

    THRESHOLD_FOR_DISTANCE = 100

    _color_cache = {}
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

    def get_potential_state_frame_meter(self) -> Optional[StateFrameMeterEnum]:
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
