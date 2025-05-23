import { readdirSync } from "fs";
import { basename, join, relative } from "path";

import { MockInstance } from "vitest";

const fixtureDir = join(
  __dirname,
  "..",
  "..",
  "..",
  "..",
  "codegen_integration",
  "fixtures"
);

const allFixtures = readdirSync(fixtureDir);

function getFixtures(
  excludeFixtures: Set<string> | string[] = new Set(),
  includeFixtures: Set<string> | string[] = new Set()
): string[] {
  const excludeSet = Array.isArray(excludeFixtures)
    ? new Set(excludeFixtures)
    : excludeFixtures;
  const includeSet = Array.isArray(includeFixtures)
    ? new Set(includeFixtures)
    : includeFixtures;

  return allFixtures.filter((f) => {
    const fileName = basename(f);

    return (
      (!excludeSet.size || !excludeSet.has(fileName)) &&
      (!includeSet.size || includeSet.has(fileName))
    );
  });
}

function getFixturePaths(root: string) {
  const displayFile = join(
    fixtureDir,
    root,
    "display_data",
    `${basename(root)}.json`
  );
  const codeDir = join(fixtureDir, root, "code");

  return { displayFile, codeDir };
}

export function getFixturesForProjectTest(
  {
    excludeFixtures,
    includeFixtures,
    fixtureMocks,
  }: {
    excludeFixtures?: Set<string> | string[];
    includeFixtures?: Set<string> | string[];
    fixtureMocks?: Record<string, MockInstance>;
  } = {
    excludeFixtures: new Set(),
    includeFixtures: new Set(),
    fixtureMocks: {},
  }
): {
  fixtureName: string;
  displayFile: string;
  codeDir: string;
  mock?: MockInstance;
}[] {
  return getFixtures(excludeFixtures, includeFixtures).map((root) => ({
    fixtureName: root,
    ...getFixturePaths(root),
    mock: fixtureMocks?.[root],
  }));
}

export function getAllFilesInDir(
  dirPath: string,
  ignoreRegexes?: RegExp[]
): { [relativePath: string]: string } {
  const files: { [relativePath: string]: string } = {};

  function traverseDir(currentPath: string) {
    const entries = readdirSync(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = join(currentPath, entry.name);

      if (entry.isDirectory()) {
        traverseDir(fullPath);
      } else if (entry.isFile()) {
        const relativePath = relative(dirPath, fullPath);

        if (
          ignoreRegexes &&
          ignoreRegexes.some((regex) => regex.test(relativePath))
        ) {
          continue;
        }

        files[relativePath] = fullPath;
      }
    }
  }

  traverseDir(dirPath);
  return files;
}
