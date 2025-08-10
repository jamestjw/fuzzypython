import argparse
import os
import pathlib

from sortedcontainers import SortedList

MATCH_SCORE = 12
MISMATCH_PENALTY = 6
GAP_OPEN_PENALTY = 5
GAP_EXTEND_PENALTY = 1


def build_scores(needle, haystack):
    num_rows, num_cols = len(needle) + 1, len(haystack) + 1
    prev = [0] * num_cols
    curr = [0] * num_cols
    max_val = 0

    for i in range(1, num_rows):
        needle_char = needle[i - 1]
        insert_gap_mask = True
        delete_gap_mask = True

        for j in range(1, num_cols):
            haystack_char = haystack[j - 1]
            match_score = prev[j - 1] + (
                MATCH_SCORE if needle_char == haystack_char else -MISMATCH_PENALTY
            )
            # left
            delete_gap_penalty = (
                GAP_OPEN_PENALTY if delete_gap_mask else GAP_EXTEND_PENALTY
            )
            delete = prev[j] - delete_gap_penalty
            # up
            insert_gap_penalty = (
                GAP_OPEN_PENALTY if insert_gap_mask else GAP_EXTEND_PENALTY
            )
            insert = curr[j - 1] - insert_gap_penalty

            max_score = max(match_score, delete, insert)

            match_mask = max_score == match_score
            insert_gap_mask = (max_score != insert) or match_mask
            delete_gap_mask = (max_score != delete) or match_mask

            curr[j] = max_score
            max_val = max(curr[j], max_val)

        prev = curr
        curr = [0] * num_cols

    return max_val


def fuzzy_match(query, candidate):
    return build_scores(candidate.lower(), query.lower())


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
            if score > 0:
                results.add((score, d))

    for _, d in results:
        print(d)


if __name__ == "__main__":
    main()
