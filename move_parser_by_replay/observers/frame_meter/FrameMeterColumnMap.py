from typing import Optional, Self, List

from move_parser_by_replay.base.Player import Player
from move_parser_by_replay.observers.LikelihoodMapForObservation import LikelihoodMapForObservation
from move_parser_by_replay.observers.frame_meter.StateFrameMeter import StateFrameMeter
from move_parser_by_replay.observers.frame_meter.StateFrameMeterRegistry import StateFrameMeterRegistry
from move_parser_by_replay.observers.frame_meter.StateType import StateType
from move_parser_by_replay.observers.frame_meter.TemporalState import TemporalState


class FrameMeterColumnMap:
    NOTHING_STATE = StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PRESENT)
    NOTHING_PAST_STATE = StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PRESENT)
    END_WINDOW = StateFrameMeterRegistry.get(StateType.FRAME_METER_END_OF_FULL_WINDOW, TemporalState.PRESENT)

    THRESHOLD_PAST_PROBABILITY = 0.2
    THRESHOLD_PRESENT_PROBABILITY = THRESHOLD_PAST_PROBABILITY
    THRESHOLD_UNKNOWN_PROBABILITY = 0.5
    THRESHOLD_END_WINDOW_PROBABILITY = 0.5

    PROBABILITY_NOTHING_CONFUSES_PAST_PRESENT = 1 / 80  # The "index" rectangle appears differently

    p1_state: LikelihoodMapForObservation[StateFrameMeter]
    p2_state: LikelihoodMapForObservation[StateFrameMeter]
    column_position: int

    def __init__(self, column_position: int,
                 p1_state: LikelihoodMapForObservation[StateFrameMeter] = None,
                 p2_state: LikelihoodMapForObservation[StateFrameMeter] = None):
        self.p1_state = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(p1_state)
        self.p2_state = LikelihoodMapForObservation.get_new_likelihood_map_if_value_is_none(p2_state)
        self.column_position = column_position

    def is_past(self) -> bool:
        return self.probability_that_is_past() >= self.THRESHOLD_PAST_PROBABILITY

    def is_present(self) -> bool:
        return self.probability_that_is_present() >= self.THRESHOLD_PRESENT_PROBABILITY

    def probability_that_is_past(self) -> float:
        p1_past_probability = self.get_probability_of_a_state_being_past(self.p1_state)
        p2_past_probability = self.get_probability_of_a_state_being_past(self.p2_state)
        return p1_past_probability * p2_past_probability

    def probability_that_is_present(self) -> float:
        p1_present_probability = self.get_probability_of_a_state_being_present(self.p1_state)
        p2_present_probability = self.get_probability_of_a_state_being_present(self.p2_state)
        return p1_present_probability * p2_present_probability

    @classmethod
    def get_probability_of_a_state_being_past(cls, state: LikelihoodMapForObservation[StateFrameMeter]) -> float:
        dictionary_of_possibilities = state.get_dictionary_of_possibilities()
        is_past_weight = state.get_unknown_weight()
        for possibility in dictionary_of_possibilities:
            if possibility.is_from_the_past():
                is_past_weight += dictionary_of_possibilities[possibility]
            elif possibility.is_nothing():
                is_past_weight += dictionary_of_possibilities[possibility] \
                                  * cls.PROBABILITY_NOTHING_CONFUSES_PAST_PRESENT
        probability = is_past_weight / state.get_total_weight()
        return probability

    @classmethod
    def get_probability_of_a_state_being_present(cls, state: LikelihoodMapForObservation[StateFrameMeter]) -> float:
        dictionary_of_possibilities = state.get_dictionary_of_possibilities()
        is_present_weight = state.get_unknown_weight()
        for possibility in dictionary_of_possibilities:
            if possibility.is_from_the_present():
                is_present_weight += dictionary_of_possibilities[possibility]
            elif possibility.is_nothing():
                is_present_weight += dictionary_of_possibilities[possibility] \
                                     * cls.PROBABILITY_NOTHING_CONFUSES_PAST_PRESENT
        probability = is_present_weight / state.get_total_weight()
        return probability

    def is_unknown_or_nothing(self) -> bool:
        return self.probability_is_unknown_or_nothing() >= self.THRESHOLD_UNKNOWN_PROBABILITY

    def probability_is_unknown_or_nothing(self) -> float:
        return self.is_specific_state_unknown_or_nothing(self.p1_state) * \
            self.is_specific_state_unknown_or_nothing(self.p2_state)

    def is_end_of_window(self) -> bool:
        return self.probability_is_end_of_window() >= self.THRESHOLD_END_WINDOW_PROBABILITY

    def probability_is_end_of_window(self) -> float:
        return self.p1_state.get_likelihood_for_observation(self.END_WINDOW) * \
            self.p2_state.get_likelihood_for_observation(self.END_WINDOW)

    def get_state_for_player(self, player: Player) -> LikelihoodMapForObservation[StateFrameMeter]:
        if player == Player.FIRST_PLAYER:
            return self.p1_state
        return self.p2_state

    def get_column_position(self) -> int:
        return self.column_position

    def set_state_for_player(self, player: Player, state: LikelihoodMapForObservation[StateFrameMeter]) -> None:
        if player == Player.FIRST_PLAYER:
            self.p1_state = state
        else:
            self.p2_state = state

    def transform_from_past_to_present(self) -> Self:
        new_p1_state = self.transform_likelihood_to_present(self.p1_state)
        new_p2_state = self.transform_likelihood_to_present(self.p2_state)

        return FrameMeterColumnMap(self.column_position, new_p1_state, new_p2_state)

    @staticmethod
    def transform_likelihood_to_present(state: LikelihoodMapForObservation[StateFrameMeter]) -> \
            LikelihoodMapForObservation[StateFrameMeter]:
        new_likelihood: LikelihoodMapForObservation[StateFrameMeter] = LikelihoodMapForObservation(
            total_weight=state.get_unknown_weight())
        for possibility, weight in state.get_dictionary_of_possibilities().items():
            new_likelihood.add_observation(possibility.to_present(), weight=weight)
        return new_likelihood

    @staticmethod
    def is_specific_state_from_past(state: Optional[StateFrameMeter]) -> bool:
        return state is not None and state.is_from_the_past()

    @staticmethod
    def is_specific_state_unknown_or_nothing(state: LikelihoodMapForObservation[StateFrameMeter]) -> float:
        return state.get_likelihood_for_observation(None) \
            + state.get_likelihood_for_observation(
                StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PRESENT)) \
            + state.get_likelihood_for_observation(StateFrameMeterRegistry.get(StateType.NOTHING, TemporalState.PAST))

    @classmethod
    def get_end_window_column(cls):
        return cls(81, LikelihoodMapForObservation(default_value=cls.END_WINDOW),
                   LikelihoodMapForObservation(default_value=cls.END_WINDOW))

    def __hash__(self):
        return hash((self.p1_state, self.p2_state, self.column_position))

    def __eq__(self, other: Self) -> bool:
        return self.p1_state == other.p1_state and self.p2_state == other.p2_state and \
            self.column_position == other.column_position

    def __repr__(self) -> str:
        return "P1 state {}, P2 state {}, column {}".format(str(self.p1_state), str(self.p2_state),
                                                            str(self.column_position))

    def get_differences_with_other(self, other: Self) -> List[str]:
        differences = []

        self_p1 = self.p1_state.get_known_most_likely_possibility()
        other_p1 = other.p1_state.get_known_most_likely_possibility()
        if self_p1 != other_p1:
            differences.append('P1 State, {} vs {}'.format(str(self_p1), str(other_p1)))

        self_p2 = self.p2_state.get_known_most_likely_possibility()
        other_p2 = other.p2_state.get_known_most_likely_possibility()
        if self_p2 != other_p2:
            differences.append('P2 State, {} vs {}'.format(str(self_p2), str(other_p2)))

        return differences

    def merge_with_other_column(self, other: Self) -> Self:
        if self.column_position != other.column_position:
            raise Exception(
                'You tried to merge two columns that are not in the same position {} vs {}'.format(self.column_position,
                                                                                                   other.column_position))
        new_p1_state = self.p1_state.get_merge_map_with_second_map(other.p1_state)
        new_p2_state = self.p2_state.get_merge_map_with_second_map(other.p2_state)

        return FrameMeterColumnMap(self.column_position, new_p1_state, new_p2_state)

    def probability_is_same_frame_meter_column_than(self, other: Self) -> float:
        if self.column_position != other.column_position:
            return 0
        p1_same_probability = self.p1_state.get_probability_this_object_is_the_same_than(other.p1_state)
        p2_same_probability = self.p2_state.get_probability_this_object_is_the_same_than(other.p2_state)
        return p1_same_probability * p2_same_probability
