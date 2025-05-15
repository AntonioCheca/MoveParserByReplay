from typing import List, Tuple, Dict, Optional

from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.framedata.Move import Move
from move_parser_by_replay.base.framedata.MoveDetectedInFrame import MoveDetectedInFrame, MoveStatus
from move_parser_by_replay.observers.frame_meter.FrameMeterObserver import FrameMeterObserver
from move_parser_by_replay.observers.frame_meter.StateType import StateType
from move_parser_by_replay.util.FrameDataReaderFromJson import FrameDataReaderFromJson


class InteractionsInMovesObserver:
    JSON_FILE_PATH = "./data/frame_data/SF6FrameData.json"

    video: Video
    frame_meter_observer: FrameMeterObserver
    guesses_p1: List[Tuple[int, Move]]
    guesses_p2: List[Tuple[int, Move]]

    def __init__(self, video: Video):
        self.video = video

        self.frame_meter_observer = FrameMeterObserver(video)
        self.frame_meter_observer.set_maximum_frame_to_look_at(2000)

    @staticmethod
    def group_consecutive_states(state_sequence: List[StateType]) -> List[Tuple[StateType, int]]:
        if not state_sequence:
            return []

        grouped = []
        current_state = state_sequence[0]
        count = 1

        for state in state_sequence[1:]:
            if state == current_state:
                count += 1
            else:
                grouped.append((current_state, count))
                current_state = state
                count = 1

        grouped.append((current_state, count))
        return grouped

    @staticmethod
    def grouped_index_to_frame(grouped_states: List[Tuple[StateType, int]], index: int) -> int:
        return sum(count for _, count in grouped_states[:index])

    @classmethod
    def find_matching_move(cls, grouped_states: List[Tuple[StateType, int]], moves: Dict[str, Move]) -> \
            Optional[Tuple[int, Move, MoveStatus]]:
        full_match = cls._find_full_match(grouped_states, moves)
        if full_match is not None:
            return full_match

        partial_match = cls._find_partial_hit_match(grouped_states, moves)
        return partial_match

    @classmethod
    def _find_full_match(cls, grouped_states: List[Tuple[StateType, int]], moves: Dict[str, Move]) -> \
            Optional[Tuple[int, Move, MoveStatus]]:
        if not grouped_states or grouped_states[0][0] != StateType.STARTUP:
            return None

        phase_order = [StateType.STARTUP, StateType.ACTIVE, StateType.RECOVERY]
        phase_counts = []
        current_phase_index = 0
        noise_frame_count = 0
        j = 0

        while j < len(grouped_states) and current_phase_index < 3:
            state, count = grouped_states[j]

            if state == phase_order[current_phase_index]:
                phase_counts.append(count)
                current_phase_index += 1
            elif state in phase_order:
                return None
            else:
                noise_frame_count += count
            j += 1

        if len(phase_counts) != 3:
            return None

        best_match = None
        best_score = float('inf')

        for move in moves.values():
            expected = move.get_list_of_state_type_frame_meter()
            if len(expected) != 3:
                continue

            diffs = [abs(observed - expected_val) for observed, expected_val in zip(phase_counts, expected)]
            total_mismatch = sum(diffs) + noise_frame_count

            if total_mismatch <= 3 and total_mismatch < best_score:
                best_score = total_mismatch
                best_match = move

        if best_match:
            return 0, best_match, MoveStatus.FULL_ANIMATION

        return None

    @classmethod
    def _find_partial_hit_match(cls, grouped_states: List[Tuple[StateType, int]], moves: Dict[str, Move]) -> \
            Optional[Tuple[int, Move, MoveStatus]]:

        if not grouped_states or grouped_states[0][0] != StateType.STARTUP:
            return None
        matched_moves = []

        if len(grouped_states) < 3:
            return None

        states = [st for st, cnt in grouped_states]
        counts = [cnt for st, cnt in grouped_states]

        if states[0] != StateType.STARTUP or states[1] != StateType.ACTIVE:
            return None

        if len(states) > 2 and states[2] == StateType.HIT_STUCK:
            hitstuck_index = 2
        elif len(states) > 3 and states[2] == StateType.RECOVERY and states[3] == StateType.HIT_STUCK:
            hitstuck_index = 3
        else:
            return None

        for move in moves.values():
            expected = move.get_list_of_state_type_frame_meter()
            if len(expected) != 3:
                continue

            expected_startup, expected_active, expected_recovery = expected

            if counts[0] != expected_startup or counts[1] != expected_active:
                continue

            recovery_count = counts[2] if states[2] == StateType.RECOVERY else 0
            if recovery_count > expected_recovery:
                continue

            matched_moves.append(move)

        if len(matched_moves) == 1:
            return 0, matched_moves[0], MoveStatus.PARTIALLY_HIT

        return None

    def analyse_full_video(self, character_p1_name: str, character_p2_name: str):
        self.frame_meter_observer.analyse_full_video()
        final_list_of_states = self.frame_meter_observer.get_final_list_for_states()

        reader = FrameDataReaderFromJson()
        characters = reader.read_json(self.JSON_FILE_PATH)

        moves_p1 = characters[character_p1_name].get_moves()
        moves_p2 = characters[character_p2_name].get_moves()

        p1_raw = [col.p1_state.get_state_type() for col in final_list_of_states if
                  col.p1_state.is_it_possible_in_final_list()]
        p2_raw = [col.p2_state.get_state_type() for col in final_list_of_states if
                  col.p2_state.is_it_possible_in_final_list()]

        p1_grouped = self.group_consecutive_states(p1_raw)
        p2_grouped = self.group_consecutive_states(p2_raw)

        guesses_p1: List[MoveDetectedInFrame] = []
        i = 0
        while i < len(p1_grouped) - 2:
            sub_group = p1_grouped[i:]
            match = self.find_matching_move(sub_group, moves_p1)
            if match:
                offset, move, status = match
                start_index = i + offset

                start_frame = self.grouped_index_to_frame(p1_grouped, start_index)
                if status == MoveStatus.FULL_ANIMATION:
                    expected_frames = move.get_list_of_state_type_frame_meter()
                    total_frames = sum(expected_frames)
                    end_frame = start_frame + total_frames
                else:
                    end_frame = start_frame
                    for j in range(start_index, min(len(p1_grouped), start_index + 5)):
                        end_frame += p1_grouped[j][1]
                        if p1_grouped[j][0] == StateType.HIT_STUCK:
                            break

                guesses_p1.append(MoveDetectedInFrame(start_frame, end_frame, move, status))
                i = start_index + (len(move.get_list_of_state_type_frame_meter()))  # move by length of move phases
            else:
                i += 1

        guesses_p2: List[MoveDetectedInFrame] = []
        i = 0
        while i < len(p2_grouped) - 2:
            sub_group = p2_grouped[i:]
            match = self.find_matching_move(sub_group, moves_p2)
            if match:
                offset, move, status = match
                start_index = i + offset

                start_frame = self.grouped_index_to_frame(p2_grouped, start_index)
                if status == MoveStatus.FULL_ANIMATION:
                    expected_frames = move.get_list_of_state_type_frame_meter()
                    total_frames = sum(expected_frames)
                    end_frame = start_frame + total_frames
                else:
                    end_frame = start_frame
                    for j in range(start_index, min(len(p2_grouped), start_index + 5)):
                        end_frame += p2_grouped[j][1]
                        if p2_grouped[j][0] == StateType.HIT_STUCK:
                            break

                guesses_p2.append(MoveDetectedInFrame(start_frame, end_frame, move, status))
                i = start_index + (len(move.get_list_of_state_type_frame_meter()))
            else:
                i += 1

        return guesses_p1, guesses_p2
