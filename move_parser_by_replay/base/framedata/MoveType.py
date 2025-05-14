from enum import Enum


class MoveType(Enum):
    NORMAL = "normal"
    SPECIAL = "special"
    SUPER = "super"
    THROW = "throw"
    DRIVE = "drive"
    MOVEMENT_SPECIAL = "movement-special"
    COMMAND_GRAB = "command-grab"
    TAUNT = "taunt"
