import argparse
import os
import pathlib
from collections import defaultdict
from typing import Optional


def fuzzy_match(query: str, candidate: str) -> Optional[int]:
    matrix: list[list[Optional[int]]] = [
        [None for _ in range(len(candidate))] for _ in range(len(query))
    ]
    candidate_char_dict = defaultdict(lambda: list())
    for i, c in enumerate(candidate):
        candidate_char_dict[c].append(i)

    prev_matches = []
    for i, q in enumerate(query):
        curr_matches = []
        if len(prev_matches) == 0:
            if i == 0:
                for j, c in enumerate(candidate):
                    if q == c:
                        matrix[i][j] = 1
                        curr_matches.append(j)
            else:
                return None
        else:
            search_start_idx = min(prev_matches)
            for candidate_idx in candidate_char_dict[q]:
                possible_scores = []
                for j in range(search_start_idx, candidate_idx):
                    old_score = matrix[i - 1][j]
                    if old_score is not None:
                        gap_penalty = candidate_idx - j - 1
                        possible_scores.append(old_score - gap_penalty)
                if possible_scores:
                    curr_matches.append(candidate_idx)
                    matrix[i][candidate_idx] = 1 + max(possible_scores)

        prev_matches = curr_matches

    scores = [int(s) for s in matrix[-1] if s is not None]
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

    results = []
    for root, _, files in search_directory.walk():
        for file in files:
            d = root / file
            score = fuzzy_match(query, d.as_posix())
            if score is not None:
                results.append((score, d))

    results.sort()

    for _, d in results:
        print(d)


if __name__ == "__main__":
    main()
