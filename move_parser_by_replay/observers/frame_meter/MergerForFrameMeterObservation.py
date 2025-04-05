from typing import List, Optional

from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


class MergerForFrameMeterObservation:
    THRESHOLD_TO_START_CHECKING_OVERLAPS = 40

    @staticmethod
    def merge_frame_meters(first_observation: FrameMeterObservation, first_frame: int,
                           second_observation: FrameMeterObservation, second_frame: int) -> \
            Optional[List[FrameMeterColumn]]:
        if second_frame - first_frame > MergerForFrameMeterObservation.THRESHOLD_TO_START_CHECKING_OVERLAPS:
            return None

        return DiffLibWrapper.merge_sequences(first_observation.get_frame_meter_list(),
                                              second_observation.get_frame_meter_list())
