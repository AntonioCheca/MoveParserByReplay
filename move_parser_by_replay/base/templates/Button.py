from move_parser_by_replay.base.templates.TemplateImage import TemplateImage


class Button(TemplateImage):
    LIGHT_KICK = 'LightKick'
    MEDIUM_KICK = 'MediumKick'
    HEAVY_KICK = 'HeavyKick'
    LIGHT_PUNCH = 'LightPunch'
    MEDIUM_PUNCH = 'MediumPunch'
    HEAVY_PUNCH = 'HeavyPunch'

    LIGHT_KICK_NUMPAD = 'lk'
    MEDIUM_KICK_NUMPAD = 'mk'
    HEAVY_KICK_NUMPAD = 'hk'
    LIGHT_PUNCH_NUMPAD = 'lp'
    MEDIUM_PUNCH_NUMPAD = 'mp'
    HEAVY_PUNCH_NUMPAD = 'hp'

    @classmethod
    def get_name_from_numpad_notation(cls, numpad_notation_raw: str) -> str:
        numpad_notation = numpad_notation_raw.lower()
        if numpad_notation == cls.LIGHT_KICK_NUMPAD.lower():
            return cls.LIGHT_KICK
        if numpad_notation == cls.MEDIUM_KICK_NUMPAD.lower():
            return cls.MEDIUM_KICK
        if numpad_notation == cls.HEAVY_KICK_NUMPAD.lower():
            return cls.HEAVY_KICK
        if numpad_notation == cls.LIGHT_PUNCH_NUMPAD.lower():
            return cls.LIGHT_PUNCH
        if numpad_notation == cls.MEDIUM_PUNCH_NUMPAD.lower():
            return cls.MEDIUM_PUNCH
        if numpad_notation == cls.HEAVY_PUNCH_NUMPAD.lower():
            return cls.HEAVY_PUNCH

        raise Exception('Numpad notation {} not recognised'.format(numpad_notation))
