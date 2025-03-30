from typing import List, Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Position import Position
from move_parser_by_replay.base.templates.TemplateImage import TemplateImage
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper
from move_parser_by_replay.util.RecognisedTemplateInPosition import RecognisedTemplateInPosition


class MatchTemplateAbstract:
    templates: Dict[str, TemplateImage]

    def __init__(self, templates: Dict[str, TemplateImage]):
        self.templates = templates

    def search_templates_in_image(self, image: Frame) -> List[RecognisedTemplateInPosition]:
        image_data = image.get_image_data()
        match_positions: List[RecognisedTemplateInPosition] = []

        for name, template in self.templates.items():
            template_data = template.get_image()
            matches = OpenCVWrapper.search_image_by_template(image_data, template_data)

            for match in matches:
                template_in_position = RecognisedTemplateInPosition(Position(int(match[0]), int(match[1])), template)
                match_positions.append(template_in_position)

        match_positions.sort(key=lambda match_in_position: match_in_position.get_position().get_inverted_tuple())

        return match_positions
