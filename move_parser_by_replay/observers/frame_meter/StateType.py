from enum import Enum


class StateType(Enum):
    ACTIVE = 'Active'
    STARTUP = 'Startup'
    RECOVERY = 'Recovery'
    FULL_INVULNERABILITY_1 = 'Full invulnerability 1'
    FULL_INVULNERABILITY_2 = 'Full invulnerability 2'
    HIT_STUCK = 'Hit Stuck'
    NUMBER_OF_FRAMES_1 = 'Number of Frames 1'
    NUMBER_OF_FRAMES_2 = 'Number of frames 2'
    NOTHING = 'Nothing'
    JUMP_OR_DASH = 'Jump or Dash'
    ARMOR_PARRY = 'Armor Parry'
    STRIKE_INVULNERABILITY_1 = 'Strike invulnerability 1'
    STRIKE_INVULNERABILITY_2 = 'Strike invulnerability 2'
    FRAME_METER_END_OF_FULL_WINDOW = 'Frame meter end of full window (Nonexistent state)'
