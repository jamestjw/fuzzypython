import argparse
import os
import pathlib

from sortedcontainers import SortedList


# def build_matrix(a, b, match_score=3, gap_cost=2):
#     num_rows, num_cols = len(a) + 1, len(b) + 1
#     H = [[0] * num_cols for _ in range(num_rows)]
#
#     # TODO: don't have to allocate the entire matrix since I only need
#     # the previous row to calculate the current row
#     for i in range(1, num_rows):
#         for j in range(1, num_cols):
#             match = H[i - 1][j - 1] + (
#                 match_score if a[i - 1] == b[j - 1] else -match_score
#             )
#             delete = H[i - 1][j] - gap_cost
#             insert = H[i][j - 1] - gap_cost
#             H[i][j] = max(match, delete, insert, 0)
#     return H
#
# def fuzzy_match_matrix(query, candidate):
#     matrix = build_matrix(candidate.lower(), query.lower())
#     return max(e for l in matrix for e in l)


# TODO: add affine gap
def build_scores(a, b, match_score=3, gap_cost=2):
    num_rows, num_cols = len(a) + 1, len(b) + 1
    prev = [0] * num_cols
    curr = [0] * num_cols
    max_val = 0

    for i in range(1, num_rows):
        for j in range(1, num_cols):
            match = prev[j - 1] + (
                match_score if a[i - 1] == b[j - 1] else -match_score
            )
            delete = prev[j] - gap_cost
            insert = curr[j - 1] - gap_cost
            curr[j] = max(match, delete, insert, 0)

        max_val = max(max(curr), max_val)
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
