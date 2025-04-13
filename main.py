import argparse
import os
import pathlib
from collections import OrderedDict, defaultdict
from typing import Optional

from sortedcontainers import SortedList


def fuzzy_match(query: str, candidate: str) -> Optional[int]:
    # Use a nested dictionary instead of an actual matrix for performance
    matrix = defaultdict(lambda: OrderedDict())
    candidate_char_dict = defaultdict(lambda: list())
    for i, c in enumerate(candidate):
        candidate_char_dict[c].append(i)

    prev_first_match: Optional[int] = None
    for i, q in enumerate(query):
        curr_first_match: Optional[int] = None
        if i == 0:
            candidate_idxs = candidate_char_dict[q]
            curr_first_match = candidate_idxs[0] if candidate_idxs else None
            for j in candidate_idxs:
                matrix[i][j] = 1
        else:
            if prev_first_match is None:
                return None
            for candidate_idx in candidate_char_dict[q]:
                possible_scores = []

                for j in matrix[i - 1].keys():
                    if prev_first_match <= j < candidate_idx:
                        old_score = matrix[i - 1][j]
                        gap_penalty = candidate_idx - j - 1
                        possible_scores.append(old_score - gap_penalty)
                    else:
                        break

                if possible_scores:
                    curr_first_match = (
                        candidate_idx
                        if curr_first_match is None
                        else min(candidate_idx, curr_first_match)
                    )
                    matrix[i][candidate_idx] = 1 + max(possible_scores)

        prev_first_match = curr_first_match

    scores = list(matrix[len(query) - 1].values())
    return max(scores) if scores else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("directory", default=os.getcwd(), nargs="?", type=pathlib.Path)
    args = parser.parse_args()

    query: str = args.query
    search_directory: pathlib.Path = args.directory

    if not search_directory.is_dir():
        raise Exception("invalid search directory")

    results = SortedList()
    for root, _, files in os.walk(search_directory):
        for file in files:
            d = os.path.join(root, file)
            score = fuzzy_match(query, d)
            if score is not None:
                results.add((score, d))

    for _, d in results:
        print(d)


if __name__ == "__main__":
    main()
