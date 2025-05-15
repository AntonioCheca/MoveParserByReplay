from typing import Dict, Optional, Any
import json

from move_parser_by_replay.base.Character import Character
from move_parser_by_replay.base.framedata.AttackLevel import AttackLevel
from move_parser_by_replay.base.framedata.InputNotation import InputNotation
from move_parser_by_replay.base.framedata.Move import Move
from move_parser_by_replay.base.framedata.MoveType import MoveType


class FrameDataReaderFromJson:
    @staticmethod
    def read_json(json_file_path: str) -> Dict[str, Character]:
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading JSON file: {e}")
            return {}

        characters = {}

        for character_name, character_data in data.items():
            character = Character(character_name)

            if "moves" not in character_data:
                continue

            for move_type_str, moves in character_data["moves"].items():
                try:
                    move_type = MoveType(move_type_str.lower())
                except ValueError:
                    continue

                for move_name, move_data in moves.items():
                    move = FrameDataReaderFromJson._create_move(move_name, move_type, move_data)
                    if move:
                        character.moves[move_name] = move

            characters[character_name] = character

        return characters

    @staticmethod
    def _create_move(move_name: str, move_type: MoveType, move_data: Dict[str, Any]) -> Optional[Move]:
        required_fields = {
            "moveName": str,
            "startup": int,
            "active": int,
            "recovery": int,
            "total": int
        }

        for field, expected_type in required_fields.items():
            if field not in move_data:
                return None

            if field == "moveName" and not isinstance(move_data[field], str):
                return None

            if field in ["startup", "active", "recovery", "total"]:
                if isinstance(move_data[field], int):
                    continue
                elif isinstance(move_data[field], str):
                    if move_data[field].isdigit():
                        move_data[field] = int(move_data[field])
                    else:
                        return None
                elif isinstance(move_data[field], float):
                    move_data[field] = int(move_data[field])
                else:
                    return None

        input_notation = InputNotation(
            plain_command=move_data.get("plnCmd", ""),
            numpad_notation=move_data.get("numCmd", ""),
            easy_command=move_data.get("ezCmd", "")
        )

        attack_level = AttackLevel.UNKNOWN
        if "atkLvl" in move_data and move_data["atkLvl"] in [level.value for level in AttackLevel]:
            for level in AttackLevel:
                if level.value == move_data["atkLvl"]:
                    attack_level = level
                    break

        damage_scaling = move_data.get("dmgScaling", "")

        hitstun = None
        if "hitstun" in move_data and isinstance(move_data["hitstun"], (int, float)):
            hitstun = int(move_data["hitstun"])

        blockstun = None
        if "blockstun" in move_data and isinstance(move_data["blockstun"], (int, float)):
            blockstun = int(move_data["blockstun"])

        hitstop = None
        if "hitstop" in move_data and isinstance(move_data["hitstop"], (int, float)):
            hitstop = int(move_data["hitstop"])

        cancellable_into = move_data.get("xx", None)

        move = Move(
            move_name=move_name,
            move_type=move_type,
            input_notation=input_notation,
            startup_frames=move_data["startup"],
            active_frames=move_data["active"],
            recovery_frames=move_data["recovery"],
            total_frames=move_data["total"],
            attack_level=attack_level,
            damage_scaling=damage_scaling,
            hitstun=hitstun,
            blockstun=blockstun,
            hitstop=hitstop,
            cancellable_into=cancellable_into
        )

        return move
