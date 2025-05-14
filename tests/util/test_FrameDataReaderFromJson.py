import pytest
import os

from move_parser_by_replay.base.Character import Character
from move_parser_by_replay.base.framedata.Move import Move
from move_parser_by_replay.base.framedata.MoveType import MoveType
from move_parser_by_replay.util.FrameDataReaderFromJson import FrameDataReaderFromJson


def test_frame_data_reader():
    json_file_path = "./data/frame_data/SF6FrameData.json"

    if not os.path.exists(json_file_path):
        pytest.skip(f"Test file not found: {json_file_path}")

    reader = FrameDataReaderFromJson()
    characters = reader.read_json(json_file_path)

    assert len(characters) > 0, "No characters were loaded from the JSON file"

    for character in characters:
        assert isinstance(character, Character)
        assert isinstance(character.name, str)
        assert len(character.name) > 0, f"Character has empty name"
        assert len(character.moves) > 0, f"Character {character.name} has no moves"

        for move_name, move in character.moves.items():
            assert isinstance(move, Move)
            assert isinstance(move.move_name, str)
            assert isinstance(move.move_type, MoveType)
            assert isinstance(move.startup_frames, int)
            assert isinstance(move.active_frames, int)
            assert isinstance(move.recovery_frames, int)
            assert isinstance(move.total_frames, int)
            assert move.input_notation is not None
            if move.cancellable_into is not None:
                assert isinstance(move.cancellable_into, list)


def test_specific_move_details():
    json_file_path = "./data/frame_data/SF6FrameData.json"
    if not os.path.exists(json_file_path):
        pytest.skip(f"Test file not found: {json_file_path}")

    reader = FrameDataReaderFromJson()
    characters = reader.read_json(json_file_path)

    aki = next((character for character in characters if character.name == "A.K.I."), None)

    if aki is None:
        pytest.skip("A.K.I. character not found in the JSON data")

    assert "Stand LP" in aki.moves, "A.K.I. should have a 'Stand LP' move"

    stand_lp = aki.moves["Stand LP"]

    assert stand_lp.move_name == "Stand LP"
    assert stand_lp.startup_frames == 5
    assert stand_lp.active_frames == 2
    assert stand_lp.recovery_frames == 7
    assert stand_lp.total_frames == 13

    assert stand_lp.hitstun == 13
    assert stand_lp.blockstun == 8
    assert stand_lp.hitstop == 9

    assert stand_lp.input_notation.plain_command == "LP"
    assert stand_lp.input_notation.numpad_notation == "5LP"
    assert stand_lp.input_notation.easy_command == "L"

    assert isinstance(stand_lp.cancellable_into, list)
    assert "sp" in stand_lp.cancellable_into
    assert "su" in stand_lp.cancellable_into
    assert "tc" in stand_lp.cancellable_into
