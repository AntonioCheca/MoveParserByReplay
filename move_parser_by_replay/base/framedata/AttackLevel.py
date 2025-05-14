from enum import Enum


class AttackLevel(Enum):
    HIGH = "H"
    MID = "M"
    LOW = "L"
    THROW = "T"
    OVERHEAD = "O"
    SPECIAL = "S"
    UNKNOWN = ""
