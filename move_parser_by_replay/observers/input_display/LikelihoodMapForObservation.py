from typing import TypeVar, Generic, Dict, Optional, Self

T = TypeVar('T')


class LikelihoodMapForObservation(Generic[T]):
    weights_for_observations = Dict[Optional[T], int]
    total_weight: int

    def __init__(self, likelihood_for_possibilities: Dict[Optional[T], int] = None,
                 total_weight: Optional[int] = None):
        if likelihood_for_possibilities is not None:
            self.weights_for_observations = likelihood_for_possibilities

            if total_weight is None:
                raise Exception('You cannot create LikelihoodMap from another likelihood map without the count')
            self.total_weight = total_weight
        else:
            self.total_weight = 0
            self.weights_for_observations = {}
            self.add_observation(None)

    def get_dictionary_of_possibilities(self) -> Dict[Optional[T], int]:
        return self.weights_for_observations

    def add_observation(self, observation: Optional[T], weight: int = 1) -> None:
        if observation not in self.weights_for_observations:
            self.weights_for_observations[observation] = 0

        self.weights_for_observations[observation] += weight
        self.total_weight += weight

    def get_likelihood_for_observation(self, observation: Optional[T]) -> float:
        if observation not in self.weights_for_observations:
            return 0

        return self.weights_for_observations[observation] / self.total_weight

    @classmethod
    def get_new_likelihood_map_if_value_is_none(cls, likelihood_map: Self) -> Self:
        if likelihood_map is None:
            return cls()

        return likelihood_map
