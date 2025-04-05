from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.observers.character.CharacterObserver import CharacterTemplateObserver


def test_character_observer_in_basic_video():
    video = Video('./data/match1.mkv')
    character_observer = CharacterTemplateObserver(video)
    character_observer.fill_from_video()

    characters = character_observer.get_character_guesses()
    expected_p1 = 'zangief'
    expected_p2 = 'cammy'

    assert expected_p1 == characters[Player.FIRST_PLAYER]
    assert expected_p2 == characters[Player.SECOND_PLAYER]
