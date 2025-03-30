# match_preprocessor.py
from typing import List
from move_parser_by_replay.base.Video import Video
from move_parser_by_replay.base.Frame import Frame


class MatchPreProcessor:
    file_path: str
    video: Video
    input_display_p1: InputDisplay
    input_display_p2: InputDisplay
    round_victory_observer_p1: RoundVictoryObserver
    round_victory_observer_p2: RoundVictoryObserver
    frame_meter_observer: FrameMeterObserver
    timer_round_observer: TimerRoundObserver
    character_observer_p1: CharacterObserver
    character_observer_p2: CharacterObserver
    life_observer_p1: LifeObserver
    life_observer_p2: LifeObserver
    super_meter_observer_p1: SuperMeterObserver
    super_meter_observer_p2: SuperMeterObserver
    character_damage_observer_p1: CharacterDamageObserver
    character_damage_observer_p2: CharacterDamageObserver

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.video = Video(file_path)

        # Initialize all observers with appropriate regions
        # These values should be determined based on the game's resolution
        # Using placeholders here
        p1_input_region = (50, 650, 200, 100)
        p2_input_region = (1000, 650, 200, 100)

        p1_round_victory_region = (500, 50, 50, 30)
        p2_round_victory_region = (700, 50, 50, 30)

        frame_meter_region = (600, 30, 80, 30)
        timer_region = (640, 80, 60, 30)

        p1_character_region = (100, 80, 200, 100)
        p2_character_region = (980, 80, 200, 100)

        p1_life_region = (200, 120, 300, 30)
        p2_life_region = (780, 120, 300, 30)

        p1_super_meter_region = (200, 150, 300, 30)
        p2_super_meter_region = (780, 150, 300, 30)

        p1_damage_region = (200, 200, 100, 50)
        p2_damage_region = (900, 200, 100, 50)

        self.input_display_p1 = InputDisplay(1, p1_input_region)
        self.input_display_p2 = InputDisplay(2, p2_input_region)

        self.round_victory_observer_p1 = RoundVictoryObserver(1, p1_round_victory_region)
        self.round_victory_observer_p2 = RoundVictoryObserver(2, p2_round_victory_region)

        self.frame_meter_observer = FrameMeterObserver(frame_meter_region)
        self.timer_round_observer = TimerRoundObserver(timer_region)

        self.character_observer_p1 = CharacterObserver(1, p1_character_region)
        self.character_observer_p2 = CharacterObserver(2, p2_character_region)

        self.life_observer_p1 = LifeObserver(1, p1_life_region)
        self.life_observer_p2 = LifeObserver(2, p2_life_region)

        self.super_meter_observer_p1 = SuperMeterObserver(1, p1_super_meter_region)
        self.super_meter_observer_p2 = SuperMeterObserver(2, p2_super_meter_region)

        self.character_damage_observer_p1 = CharacterDamageObserver(1, p1_damage_region)
        self.character_damage_observer_p2 = CharacterDamageObserver(2, p2_damage_region)

    def initialize_and_fill_observers(self) -> None:
        self.input_display_p1.fill_from_video(self.video)
        self.input_display_p2.fill_from_video(self.video)

        self.round_victory_observer_p1.fill_from_video(self.video)
        self.round_victory_observer_p2.fill_from_video(self.video)

        self.frame_meter_observer.fill_from_video(self.video)
        self.timer_round_observer.fill_from_video(self.video)

        self.character_observer_p1.fill_from_video(self.video)
        self.character_observer_p2.fill_from_video(self.video)

        self.life_observer_p1.fill_from_video(self.video)
        self.life_observer_p2.fill_from_video(self.video)

        self.super_meter_observer_p1.fill_from_video(self.video)
        self.super_meter_observer_p2.fill_from_video(self.video)

        self.character_damage_observer_p1.fill_from_video(self.video)
        self.character_damage_observer_p2.fill_from_video(self.video)

    def is_new_in_game_frame(self, frame: Frame) -> bool:
        # Implementation will depend on how we determine new frames
        # Could use frame meter observer
        pass

    def is_round_in_progress(self, frame: Frame) -> bool:
        # Check if this frame is part of an active round
        # Could use timer, life bars, etc.
        pass

    def process_video(self) -> List[Frame]:
        self.initialize_and_fill_observers()

        processed_frames = []
        current_frame_number = 0
        has_more_frames = True

        while has_more_frames:
            frame = self.video.get_frame(current_frame_number)

            if frame is None:
                has_more_frames = False
                continue

            if self.is_round_in_progress(frame) and self.is_new_in_game_frame(frame):
                processed_frames.append(frame)

            current_frame_number += 1

        return processed_frames

    def save_processed_video(self, output_path: str) -> None:
        # Implementation to save the processed frames as a new video
        pass
