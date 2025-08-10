import argparse
import bisect
import os
import pathlib
import re

MATCH_SCORE = 12
MISMATCH_PENALTY = 6
GAP_OPEN_PENALTY = 5
GAP_EXTEND_PENALTY = 1
CAPITALIZATION_BONUS = 4
MATCHING_CASE_BONUS = 4
EXACT_MATCH_BONUS = 8
PREFIX_BONUS = 12
OFFSET_PREFIX_BONUS = 8
DELIMITER_BONUS = 4

DELIMITER_REGEX = re.compile(f" |/|\\.|,|_|-|:")


def build_scores(needle, haystack):
    num_rows, num_cols = len(needle) + 1, len(haystack) + 1
    prev = [0] * num_cols
    curr = [0] * num_cols
    max_val = 0

    for i in range(1, num_rows):
        needle_char = needle[i - 1]
        needle_is_uppercase = needle_char.isupper()
        needle_char = needle_char.lower()

        delimiter_bonus_enabled = False
        prev_haystack_is_delimiter = False
        insert_gap_mask = True
        delete_gap_mask = True
        prev_haystack_is_lowercase = False

        for j in range(1, num_cols):
            # Is first letter?
            is_prefix = j == 1
            # Is the first letter some kind of delimiter like an underscore,
            # and that we didn't match on it previously?
            is_offset_prefix = (
                j == 2
                and prev[1] == 0
                and not (haystack[0].isalpha() and haystack[0].isascii())
            )

            haystack_char = haystack[j - 1]
            haystack_is_uppercase = haystack_char.isupper()
            haystack_is_lowercase = haystack_char.islower()
            haystack_is_delimiter = bool(DELIMITER_REGEX.match(haystack_char))
            haystack_char = haystack_char.lower()

            matched_cased_mask = needle_is_uppercase == haystack_is_uppercase

            if needle_char == haystack_char:
                if is_prefix:
                    match_score = prev[j - 1] + MATCH_SCORE + PREFIX_BONUS
                elif is_offset_prefix:
                    match_score = prev[j - 1] + MATCH_SCORE + OFFSET_PREFIX_BONUS
                else:
                    match_score = prev[j - 1] + MATCH_SCORE

                if (
                    prev_haystack_is_delimiter
                    and delimiter_bonus_enabled
                    and not haystack_is_delimiter
                ):
                    match_score += DELIMITER_BONUS

                # Bonus if the case matches
                if matched_cased_mask:
                    match_score += MATCHING_CASE_BONUS

                # Bonus when matching on a capital letter
                if (
                    not is_prefix
                    and haystack_is_uppercase
                    and prev_haystack_is_lowercase
                ):
                    match_score += CAPITALIZATION_BONUS
            else:
                match_score = prev[j - 1] - MISMATCH_PENALTY

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

            prev_haystack_is_lowercase = haystack_is_lowercase
            prev_haystack_is_delimiter = haystack_is_delimiter
            # This will only be enabled if we have seen a non-delimiter char,
            # i.e. we don't want to apply the bonus if the string starts with a series
            # of delimiter characters
            delimiter_bonus_enabled |= not prev_haystack_is_delimiter

        prev = curr
        curr = [0] * num_cols

    max_score = max_val

    if haystack == needle:
        max_score += EXACT_MATCH_BONUS

    return max_score


def fuzzy_match(query, candidate):
    return build_scores(candidate, query)


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
    for root, _, files in os.walk(search_directory):
        for file in files:
            d = os.path.join(root, file)
            score = fuzzy_match(query, d)
            if score > 0:
                # lexical sort ensures that this is right
                bisect.insort(results, (score, d))

    for _, d in results:
        print(d)


if __name__ == "__main__":
    main()
