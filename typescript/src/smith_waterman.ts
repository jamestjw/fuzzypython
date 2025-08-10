#!/usr/bin/env ts-node

import { argv } from "process";
import { promises as fs } from "fs";
import * as path from "path";

const MATCH_SCORE = 12;
const MISMATCH_PENALTY = 6;
const GAP_OPEN_PENALTY = 5;
const GAP_EXTEND_PENALTY = 1;
const CAPITALIZATION_BONUS = 4;
const MATCHING_CASE_BONUS = 4;
const EXACT_MATCH_BONUS = 8;
const PREFIX_BONUS = 12;
const OFFSET_PREFIX_BONUS = 8;
const DELIMITER_BONUS = 4;

const DELIMITERS = [" ", "/", ".", ",", "_", "-", ":"];

function isAsciiAlphabetic(str: string) {
  // This regex checks if the string contains ONLY a-z and A-Z characters
  // from the beginning (^) to the end ($).
  const regex = /^[a-zA-Z]+$/;
  return regex.test(str);
}

function smithWaterman(needle: string, haystack: string) {
  const numRows = needle.length + 1;
  const numCols = haystack.length + 1;
  let prev: number[] = new Array(numCols).fill(0);
  let curr: number[] = new Array(numCols).fill(0);
  let maxVal = 0;

  for (let i = 1; i < numRows; i++) {
    let needleChar = needle[i - 1];
    const needleIsUppercase = needleChar.toUpperCase() == needleChar;
    needleChar = needleChar.toLowerCase();

    // Only enabled if we have already encountered a non-delimiter
    // character in the haystack
    let delimiterBonusEnabled = false;
    let prevHaystackIsDelimiter = false;
    let insertGapMask = true;
    let deletegapMask = true;
    let prevHaystackIsLowercase = false;

    for (let j = 1; j < numCols; j++) {
      // Is first letter?
      const isPrefix = j == 1;
      // Is the first letter some kind of delimiter like an underscore,
      // and that we didn't match on it previously?
      const isOffsetPrefix =
        j == 2 && prev[1] == 0 && !isAsciiAlphabetic(haystack[0]);

      let haystackChar = haystack[j - 1];
      const haystackIsUppercase = haystackChar.toUpperCase() == haystackChar;
      const haystackIsLowercase = haystackChar.toLowerCase() == haystackChar;
      const haystackIsDelimiter = DELIMITERS.some((d) => d == haystackChar);
      haystackChar = haystackChar.toLowerCase();

      const matchedCasedMask = needleIsUppercase == haystackIsUppercase;

      let matchScore;
      if (needleChar == haystackChar) {
        if (isPrefix) matchScore = prev[j - 1] + MATCH_SCORE + PREFIX_BONUS;
        else if (isOffsetPrefix)
          matchScore = prev[j - 1] + MATCH_SCORE + OFFSET_PREFIX_BONUS;
        else matchScore = prev[j - 1] + MATCH_SCORE;

        if (
          prevHaystackIsDelimiter &&
          delimiterBonusEnabled &&
          !haystackIsDelimiter
        )
          matchScore += DELIMITER_BONUS;

        // Bonus if the case matches
        if (matchedCasedMask) matchScore += MATCHING_CASE_BONUS;

        // Bonus when matching on a capital letter
        if (!isPrefix && haystackIsUppercase && prevHaystackIsLowercase)
          matchScore += CAPITALIZATION_BONUS;
      } else matchScore = prev[j - 1] - MISMATCH_PENALTY;

      // left
      const deleteGapPenalty: number = deletegapMask
        ? GAP_OPEN_PENALTY
        : GAP_EXTEND_PENALTY;
      const deleteScore = prev[j] - deleteGapPenalty;

      // up
      const insertGapPenalty: number = insertGapMask
        ? GAP_OPEN_PENALTY
        : GAP_EXTEND_PENALTY;
      const insertScore = curr[j - 1] - insertGapPenalty;

      const maxScore = Math.max(matchScore, deleteScore, insertScore);

      const match_mask = maxScore == matchScore;
      insertGapMask = maxScore != insertScore || match_mask;
      deletegapMask = maxScore != deleteScore || match_mask;

      curr[j] = maxScore;
      maxVal = Math.max(maxScore, maxVal);

      prevHaystackIsLowercase = haystackIsLowercase;
      prevHaystackIsDelimiter = haystackIsDelimiter;
      delimiterBonusEnabled = delimiterBonusEnabled || !prevHaystackIsDelimiter;
    }

    prev = curr;
    curr = new Array(numCols).fill(0);
  }

  if (haystack == needle) maxVal += EXACT_MATCH_BONUS;

  return maxVal;
}

async function walkDir(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        return walkDir(fullPath);
      } else {
        return fullPath;
      }
    }),
  );
  return files.flat();
}

async function main() {
  const args = argv.slice(2);
  const query = args[0];
  const directory = args[1];

  const files = await walkDir(directory);

  files
    .map((file) => [file, smithWaterman(file, query)] as [string, number])
    .filter((e) => e[1] > 0)
    .sort((a, b) => a[1] - b[1])
    .forEach((e) => console.log(e[0]));
}

main();
