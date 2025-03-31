from typing import List, Iterator
import difflib


class DiffLibWrapper:
    @staticmethod
    def get_similarity_ratio_from_two_lists(first_list: List, second_list: List) -> float:
        matches = difflib.SequenceMatcher(None, tuple(first_list), tuple(second_list))
        return matches.ratio()
