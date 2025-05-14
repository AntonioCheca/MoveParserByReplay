class InputNotation:
    def __init__(self,
                 plain_command: str = "",
                 numpad_notation: str = "",
                 easy_command: str = ""
                 ):
        self.plain_command = plain_command
        self.numpad_notation = numpad_notation
        self.easy_command = easy_command

    def get_plain_command(self) -> str:
        return self.plain_command

    def get_numpad_notation(self) -> str:
        return self.numpad_notation

    def get_easy_command(self) -> str:
        return self.easy_command

    def __str__(self) -> str:
        return self.numpad_notation
