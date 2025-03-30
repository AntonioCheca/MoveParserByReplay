from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.base.Video import Video


class TimerRoundObserver:
    region: Region

    def __init__(self, region: Region):
        self.region = region

    def fill_from_video(self, video: Video) -> None:
        pass
