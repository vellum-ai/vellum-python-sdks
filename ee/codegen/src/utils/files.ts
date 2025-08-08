import { readFile, readdir } from "fs/promises";
import { join, relative } from "path";

export async function getAllFilesInDir(
  dirPath: string,
  ignoreRegexes?: RegExp[]
): Promise<{ [path: string]: string }> {
  const files: { [path: string]: string } = {};

  async function traverseDir(currentPath: string) {
    const entries = await readdir(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = join(currentPath, entry.name);

      if (entry.isDirectory()) {
        await traverseDir(fullPath);
      } else if (entry.isFile()) {
        const relativePath = relative(dirPath, fullPath);

        if (
          ignoreRegexes &&
          ignoreRegexes.some((regex) => regex.test(relativePath))
        ) {
          continue;
        }

        files[relativePath] = await readFile(fullPath, "utf-8");
      }
    }
  }

  await traverseDir(dirPath);
  return files;
}
