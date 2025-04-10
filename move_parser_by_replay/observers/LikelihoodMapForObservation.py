from typing import TypeVar, Generic, Dict, Optional, Self
import json

T = TypeVar('T')


class LikelihoodMapForObservation(Generic[T]):
    weights_for_observations = Dict[T, int]
    total_weight: int
    unknown_weight: int

    def __init__(self, likelihood_for_possibilities: Dict[Optional[T], int] = None,
                 total_weight: Optional[int] = None, default_value: Optional[T] = None):
        if likelihood_for_possibilities is not None:
            self.weights_for_observations = likelihood_for_possibilities

            if total_weight is None:
                raise Exception('You cannot create LikelihoodMap from another likelihood map without the count')
            self.total_weight = total_weight
        else:
            self.total_weight = 0
            self.unknown_weight = 0
            self.weights_for_observations = {}
            weight = total_weight if total_weight is not None else 1
            self.add_observation(observation=default_value, weight=weight)

    def get_dictionary_of_possibilities(self) -> Dict[Optional[T], int]:
        return self.weights_for_observations

    def get_total_weight(self) -> int:
        return self.total_weight

    def get_unknown_weight(self) -> int:
        return self.unknown_weight

    def add_observation(self, observation: Optional[T], weight: int = 1) -> None:
        self.total_weight += weight

        if observation is None:
            self.unknown_weight += weight
        else:
            if observation not in self.weights_for_observations:
                self.weights_for_observations[observation] = 0

            self.weights_for_observations[observation] += weight

    def get_likelihood_for_observation(self, observation: Optional[T]) -> float:
        if observation not in self.weights_for_observations:
            return 0

        return self.weights_for_observations[observation] / self.total_weight

    @classmethod
    def get_new_likelihood_map_if_value_is_none(cls, likelihood_map: Self, default_value: Optional[T] = None) -> Self:
        if likelihood_map is None:
            return cls(default_value=default_value)

        return likelihood_map

    def get_probability_this_object_is_the_same_than(self, other: Self) -> float:
        total_max_weight = self.total_weight * other.total_weight
        weight_for_being_same_object = 0
        for key in self.weights_for_observations:
            if key in other.weights_for_observations:
                weight_for_being_same_object += self.weights_for_observations[key] * other.weights_for_observations[key]

        weight_for_being_same_object += self.unknown_weight * other.total_weight
        weight_for_being_same_object += self.total_weight * other.unknown_weight

        return weight_for_being_same_object / total_max_weight

    def __eq__(self, other: Self) -> bool:
        return self.weights_for_observations == other.weights_for_observations \
            and self.total_weight == other.total_weight and self.unknown_weight == other.unknown_weight

    def __hash__(self) -> int:
        return hash((str(self), self.total_weight, self.unknown_weight))

    def __repr__(self) -> str:
        dict_with_keys_str = self.get_dict_keys_as_string()

        return json.dumps(dict_with_keys_str, sort_keys=True)

    def get_dict_keys_as_string(self):
        dict_with_keys_str = {}
        for key in self.weights_for_observations:
            dict_with_keys_str[str(key)] = self.weights_for_observations[key]
        return dict_with_keys_str

    def get_weight_for_specific_value(self, value: T) -> int:
        return self.weights_for_observations[value] if value in self.weights_for_observations else self.unknown_weight

    def get_most_likely_possibility(self) -> Optional[T]:
        most_likely_value = None
        highest_value = 0

        for key in self.weights_for_observations:
            current_value = self.weights_for_observations[key]
            if current_value > highest_value:
                highest_value = current_value
                most_likely_value = key

        return most_likely_value

    def get_merge_map_with_second_map(self, second_map: Self) -> Self:
        all_values = set(self.weights_for_observations.keys()) | set(second_map.weights_for_observations)

        new_map = LikelihoodMapForObservation(total_weight=0)
        for key in all_values:
            weight_for_first_map = self.get_weight_for_specific_value(key)
            weight_for_second_map = second_map.get_weight_for_specific_value(key)
            current_weight = weight_for_first_map * weight_for_second_map
            new_map.add_observation(key, current_weight)

        new_map.add_observation(None, weight=self.unknown_weight * second_map.get_unknown_weight())

        return new_map

    def get_best_possibility_according_to_second_map(self, second_map: Self) -> Optional[T]:
        second_map: LikelihoodMapForObservation[T]
        return self.get_merge_map_with_second_map(second_map).get_most_likely_possibility()
