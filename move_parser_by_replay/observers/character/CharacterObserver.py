from typing import Dict

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.templates.Character import Character
from move_parser_by_replay.observers.AbstractObserver import AbstractObserver
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class CharacterObserver(AbstractObserver):
    TEMPLATES_FOR_CHARACTERS = './data/characters/'
    GAP_BETWEEN_FRAMES_FOR_LOOKUP = 300

    character_templates: Dict[str, Character]
    video: Video

    characters_guesses: Dict[Player, str]

    def __init__(self, video: Video):
        self.initialise_characters()
        self.video = video
        self.characters_guesses = {}

    def initialise_characters(self) -> None:
        self.character_templates = self.load_templates_from_folder(self.TEMPLATES_FOR_CHARACTERS, Character)

    def fill_from_video(self) -> None:
        frame_position = self.GAP_BETWEEN_FRAMES_FOR_LOOKUP

        current_frame = self.video.get_frame_from_position(frame_position)
        found_p1 = False
        found_p2 = False
        while not found_p1 or not found_p2:
            for character_key in self.character_templates:
                character_template = self.character_templates[character_key]
                if self.look_for_character_in_image(character_template, current_frame):
                    if character_key[:2] == 'p1':
                        found_p1 = True
                        self.characters_guesses[Player.FIRST_PLAYER] = character_key[3:]
                    elif character_key[:2] == 'p2':
                        found_p2 = True
                        self.characters_guesses[Player.SECOND_PLAYER] = character_key[3:]
                    else:
                        raise Exception('All character templates should be either p1_* or p2_*')
            frame_position += self.GAP_BETWEEN_FRAMES_FOR_LOOKUP
            current_frame = self.video.get_frame_from_position(frame_position)

    def get_character_guesses(self) -> Dict[Player, str]:
        return self.characters_guesses

    @staticmethod
    def look_for_character_in_image(character: Character, frame: Frame) -> bool:
        matches = OpenCVWrapper.search_image_by_template(frame.get_image_data(), character.get_image())
        return len(matches) > 0
