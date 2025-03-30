from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video


class RoundVictoryObserver:
    region: Region
    player_number: int

    def __init__(self, player_number: int, region: Region):
        self.player_number = player_number
        self.region = region

    def fill_from_video(self, video: Video) -> None:
        pass
