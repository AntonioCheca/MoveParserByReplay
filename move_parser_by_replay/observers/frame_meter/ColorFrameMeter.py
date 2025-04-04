from typing import Tuple, Self, Dict, Optional

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
        StateFrameMeterEnum.JUMP_PAST: (183, 195, 57),
        StateFrameMeterEnum.HIT_STUCK_PAST: (37, 192, 185),
        StateFrameMeterEnum.FULL_INVULNERABILITY_1_PAST: (176, 176, 176),
        StateFrameMeterEnum.FULL_INVULNERABILITY_2_PAST: (144, 144, 144),
        StateFrameMeterEnum.NOTHING: (27, 24, 25),
        StateFrameMeterEnum.JUMP: (249, 255, 82),
        StateFrameMeterEnum.ARMOR_PARRY: (106, 16, 86),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1: (92, 23, 185),
        StateFrameMeterEnum.STRIKE_INVULNERABILITY_2: (251, 209, 255),
        # StateFrameMeter.STRIKE_INVULNERABILITY_1_PAST: (63, 10, 137),
        StateFrameMeterEnum.STRIKE_INVULNERABILITY_2_PAST: (184, 155, 212),
        StateFrameMeterEnum.ARMOR_PARRY_PAST: (76, 8, 60),
    }

    THRESHOLD_FOR_DISTANCE = 500

    color: Tuple[int, int, int]

    def __init__(self, color: Tuple[int, int, int]):
        self.color = color

    def get_potential_state_frame_meter(self) -> Optional[StateFrameMeterEnum]:
        for frame_state in self.ALL_COLORS:
            if self.distance_with_tuple_color(self.ALL_COLORS[frame_state]) <= self.THRESHOLD_FOR_DISTANCE:
                return frame_state
        return None

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
