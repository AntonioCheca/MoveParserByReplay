from enum import Enum
from typing import Optional, Self


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
    NOTHING_PAST = 'Nothing (Past)'
    JUMP_OR_DASH = 'Jump or Dash'
    ARMOR_PARRY = 'Armor Parry'
    STRIKE_INVULNERABILITY_1 = 'Strike invulnerability 1 (Past)'
    STRIKE_INVULNERABILITY_2 = 'Strike invulnerability 2 (Past)'
    STRIKE_INVULNERABILITY_1_PAST = 'Strike invulnerability 1 (Past)'
    STRIKE_INVULNERABILITY_2_PAST = 'Strike invulnerability 2 (Past)'
    ARMOR_PARRY_PAST = 'Armor Parry (Past)'
    FRAME_METER_END_OF_FULL_WINDOW = 'Frame meter end of full window (Nonexistent state)'

    def is_from_the_past(self) -> bool:
        return self.value[-6:] == '(Past)'

    def cannot_be_followed_by_none(self) -> bool:
        return self.value in [self.ACTIVE.value, self.STARTUP.value]

    def transform_from_past_to_present(self) -> Self:
        if self == self.NOTHING_PAST:
            return self.NOTHING
        if self == self.STARTUP_PAST:
            return self.STARTUP
        if self == self.ACTIVE_PAST:
            return self.ACTIVE
        if self == self.RECOVERY_PAST:
            return self.RECOVERY
        if self == self.HIT_STUCK_PAST:
            return self.HIT_STUCK
        if self == self.ARMOR_PARRY_PAST:
            return self.ARMOR_PARRY
        if self == self.JUMP_OR_DASH_PAST:
            return self.JUMP_OR_DASH
        if self == self.STRIKE_INVULNERABILITY_1_PAST:
            return self.STRIKE_INVULNERABILITY_1
        if self == self.STRIKE_INVULNERABILITY_2_PAST:
            return self.STRIKE_INVULNERABILITY_2
        if self == self.FULL_INVULNERABILITY_1_PAST:
            return self.FULL_INVULNERABILITY_1
        if self == self.FULL_INVULNERABILITY_2_PAST:
            return self.FULL_INVULNERABILITY_2
        return self

    def __hash__(self):
        return hash(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_csv_value(cls, csv_value: str) -> Optional[Self]:
        mapping = {
            'STARTUP': cls.STARTUP,
            'ACTIVE': cls.ACTIVE,
            'RECOVERY': cls.RECOVERY,
            'HITSTUCK': cls.HIT_STUCK,
            'NOTHING': cls.NOTHING,
            'JUMP': cls.JUMP_OR_DASH,
            'PARRY': cls.ARMOR_PARRY,
            'FULL INVULNERABILITY': cls.FULL_INVULNERABILITY_1,
            'STRIKE INVULNERABILITY': cls.STRIKE_INVULNERABILITY_1
        }

        return mapping.get(csv_value)
