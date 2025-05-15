from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.InteractionsInMovesObserver import InteractionsInMovesObserver


def test_basic_frame_meter_observer():
    video = Video('./data/match1.mkv')

    interactions_observer = InteractionsInMovesObserver(video)
    interactions_observer.analyse_full_video('Zangief', 'Cammy')

    guesses_p1 = interactions_observer.guesses_p1
    guesses_p2 = interactions_observer.guesses_p2
    assert len(guesses_p1) > 0
    assert len(guesses_p2) > 0
