from enum import Enum


class StateFrameMeterEnum(Enum):
    ACTIVE = 'Active'
    STARTUP = 'Startup'
    RECOVERY = 'Recovery'
    FULL_INVULNERABILITY_1 = 'Full invulnerability 1'
    FULL_INVULNERABILITY_2 = 'Full invulnerability 2'
    HIT_STUCK = 'Hit Stuck'
    NUMBER_OF_FRAMES_1 = 'Number of Frames 1'
    NUMBER_OF_FRAMES_2 = 'Number of frames 2'
    RECOVERY_PAST = 'Recovery (Past)'
    ACTIVE_PAST = 'Active (Past)'
    STARTUP_PAST = 'Startup (Past)'
    JUMP_OR_DASH_PAST = 'Jump or Dash (Past)'
    HIT_STUCK_PAST = 'Hit Stuck (Past)'
    FULL_INVULNERABILITY_1_PAST = 'Full Invulnerability 1 (Past)'
    FULL_INVULNERABILITY_2_PAST = 'Full Invulnerability 2 (Past)'
    NOTHING = 'Nothing'
    JUMP_OR_DASH = 'Jump or Dash'
    ARMOR_PARRY = 'Armor Parry'
    STRIKE_INVULNERABILITY_1 = 'Strike invulnerability 1 (Past)'
    STRIKE_INVULNERABILITY_2 = 'Strike invulnerability 2 (Past)'
    STRIKE_INVULNERABILITY_1_PAST = 'Strike invulnerability 1 (Past)'
    STRIKE_INVULNERABILITY_2_PAST = 'Strike invulnerability 2 (Past)'
    ARMOR_PARRY_PAST = 'Armor Parry (Past)'

    def is_from_the_past(self) -> bool:
        return self.value[-6:] == '(Past)'

    def __hash__(self):
        return hash(self.value)
