from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.templates.TemplateImage import TemplateImage


class RecognisedTemplateInPosition:
    position: Position
    template: TemplateImage

    def __init__(self, position: Position, template: TemplateImage):
        self.position = position
        self.template = template

    def get_position(self) -> Position:
        return self.position

    def get_template(self) -> TemplateImage:
        return self.template
