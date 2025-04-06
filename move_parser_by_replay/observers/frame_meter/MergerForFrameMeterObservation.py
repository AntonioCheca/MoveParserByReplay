import copy
from typing import List, Optional

from move_parser_by_replay.observers.frame_meter.FrameMeterColumn import FrameMeterColumn
from move_parser_by_replay.observers.frame_meter.FrameMeterObservation import FrameMeterObservation
from move_parser_by_replay.util.DiffLibWrapper import DiffLibWrapper


class MergerForFrameMeterObservation:
    THRESHOLD_TO_START_CHECKING_OVERLAPS = 80
    SIZE_OF_SECOND_OBSERVATION_TO_MERGE_MANUALLY = 40

    @classmethod
    def merge_frame_meters(cls, first_observation: FrameMeterObservation, first_frame: int,
                           second_observation: FrameMeterObservation, second_frame: int) -> \
            Optional[List[FrameMeterColumn]]:
        if second_frame - first_frame > MergerForFrameMeterObservation.THRESHOLD_TO_START_CHECKING_OVERLAPS:
            return None

        # if first_observation.is_last_column_end_of_window() and \
        #        len(second_observation.get_frame_meter_list()) <= cls.SIZE_OF_SECOND_OBSERVATION_TO_MERGE_MANUALLY:
        #    return cls.merge_manually(first_observation, second_observation)

        return DiffLibWrapper.merge_sequences(first_observation.get_frame_meter_list(),
                                              second_observation.get_frame_meter_list())

    @classmethod
    def merge_manually(cls, first_observation: FrameMeterObservation, second_observation: FrameMeterObservation) -> \
            List[FrameMeterColumn]:
        new_list = copy.deepcopy(first_observation.get_frame_meter_list())
        for state in second_observation.get_frame_meter_list():
            new_list.append(state)

        return new_list
