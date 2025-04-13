import argparse
import os
import pathlib
import math
from typing import Optional


def fuzzy_match(query: str, candidate: str) -> bool:
    if len(query) == 0:
        return True
    remainder = query

    for char in candidate:
        if char == remainder[0]:
            remainder = remainder[1:]
            if len(remainder) == 0:
                return True
    return False


def fuzzy_match2(query: str, candidate: str) -> Optional[int]:
    matrix : list[list[Optional[int]]] = [[None for _ in range(len(candidate))] for _ in range(len(query))]
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
            for j1, j2 in zip(prev_matches, prev_matches[1:] + [len(candidate)]):
                for j in range(j1 + 1, j2):
                    if candidate[j] == q:
                        new_score = 1 + matrix[i - 1][j1] - (j - j1 - 1)
                        old_score = matrix[i][j]
                        matrix[i][j] = new_score if old_score is None else max(old_score, new_score) 
                        curr_matches.append(j)
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
    for root, dirs, files in search_directory.walk():
        for file in files:
            d = root / file
            score = fuzzy_match2(query, d.as_posix())
            if score is not None:
                results.append((score, d))

    results.sort()

    for _, d in results:
        print(d)


if __name__ == "__main__":
    main()
