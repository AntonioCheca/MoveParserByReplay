from typing import Optional, List

from move_parser_by_replay.base.framedata.AttackLevel import AttackLevel
from move_parser_by_replay.base.framedata.InputNotation import InputNotation
from move_parser_by_replay.base.framedata.MoveType import MoveType


class Move:
    def __init__(self,
                 move_name: str,
                 move_type: MoveType,
                 input_notation: InputNotation,
                 startup_frames: int,
                 active_frames: int,
                 recovery_frames: int,
                 total_frames: int,
                 attack_level: AttackLevel = AttackLevel.UNKNOWN,
                 damage_scaling: str = "",
                 hitstun: Optional[int] = None,
                 blockstun: Optional[int] = None,
                 hitstop: Optional[int] = None,
                 cancellable_into: Optional[List[str]] = None
                 ):
        self.move_name = move_name
        self.move_type = move_type
        self.input_notation = input_notation
        self.startup_frames = startup_frames
        self.active_frames = active_frames
        self.recovery_frames = recovery_frames
        self.total_frames = total_frames
        self.attack_level = attack_level
        self.damage_scaling = damage_scaling
        self.hitstun = hitstun
        self.blockstun = blockstun
        self.hitstop = hitstop
        self.cancellable_into = cancellable_into or []

    def get_move_name(self) -> str:
        return self.move_name

    def get_move_type(self) -> MoveType:
        return self.move_type

    def get_input_notation(self) -> InputNotation:
        return self.input_notation

    def get_startup_frames(self) -> int:
        return self.startup_frames

    def get_active_frames(self) -> int:
        return self.active_frames

    def get_recovery_frames(self) -> int:
        return self.recovery_frames

    def get_total_frames(self) -> int:
        return self.total_frames

    def get_attack_level(self) -> AttackLevel:
        return self.attack_level

    def get_damage_scaling(self) -> str:
        return self.damage_scaling

    def get_hitstun(self) -> Optional[int]:
        return self.hitstun

    def get_blockstun(self) -> Optional[int]:
        return self.blockstun

    def get_hitstop(self) -> Optional[int]:
        return self.hitstop

    def get_cancellable_into(self) -> List[str]:
        return self.cancellable_into

    def get_list_of_state_type_frame_meter(self) -> List[int]:
        return [self.startup_frames - 1, self.active_frames, self.recovery_frames]

    def __str__(self) -> str:
        return self.move_name

    def __repr__(self) -> str:
        return str(self)
