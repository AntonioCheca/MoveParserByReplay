from typing import List, Iterator
import difflib


class DiffLibWrapper:
    @staticmethod
    def get_similarity_ratio_from_two_lists(first_list: List, second_list: List) -> float:
        matches = difflib.SequenceMatcher(None, tuple(first_list), tuple(second_list))
        return matches.ratio()

    @staticmethod
    def merge_sequences(a: List, b: List) -> List:
        matcher = difflib.SequenceMatcher(None, a, b)

        opcodes = matcher.get_opcodes()

        merged = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                merged.extend(a[i1:i2])
            elif tag == 'replace':
                merged.extend(a[i1:i2])
            elif tag == 'delete':
                merged.extend(a[i1:i2])
            elif tag == 'insert':
                merged.extend(b[j1:j2])

        return merged
