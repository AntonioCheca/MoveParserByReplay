from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.util.MatchTemplateAbstract import MatchTemplateAbstract


class MatchTemplateDirectionRecogniser(MatchTemplateAbstract):
    @staticmethod
    def get_subregion(frame: Frame, player: Player) -> Frame:
        if player == Player.FIRST_PLAYER:
            region = Region(90, 228, 35, 645)
        else:
            region = Region(1920 - 90 - 35, 228, 35, 645)

        return frame.get_subregion(region)
