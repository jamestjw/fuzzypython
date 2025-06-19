#!/usr/bin/env ts-node

import { argv } from "process";
import { promises as fs } from "fs";
import * as path from "path";

function smithWaterman(
  candidate: string,
  query: string,
  matchScore: number = 3,
  gapCost: number = 2,
) {
  const a = candidate.toLowerCase();
  const b = query.toLowerCase();
  const num_rows = a.length + 1;
  const num_cols = b.length + 1;
  let prev: number[] = new Array(num_cols).fill(0);
  let curr: number[] = new Array(num_cols).fill(0);
  let maxVal = 0;

  for (let i = 1; i < num_rows; i++) {
    for (let j = 1; j < num_cols; j++) {
      const match =
        prev[j - 1] + (a[i - 1] === b[j - 1] ? matchScore : -matchScore);
      const remove = prev[j] - gapCost;
      const insert = curr[j - 1] - gapCost;
      curr[j] = Math.max(match, remove, insert, 0);
    }

    maxVal = Math.max(...curr, maxVal);
    prev = curr;
    curr = new Array(num_cols).fill(0);
  }

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
