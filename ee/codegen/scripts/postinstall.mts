import { existsSync, copyFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const main = async () => {
  const sourceFile = path.join(
    __dirname,
    "..",
    "..",
    "vellum_ee",
    "assets",
    "node-definitions.json"
  );
  const targetDir = path.join(__dirname, "..", "node_modules", "vellum-ai");
  const targetFile = path.join(targetDir, "node-definitions.json");

  if (!existsSync(sourceFile)) {
    console.log("Source file does not exist, skipping postinstall copy");
    return;
  }

  if (!existsSync(targetDir)) {
    console.log("Target directory does not exist, skipping postinstall copy");
    return;
  }

  try {
    copyFileSync(sourceFile, targetFile);
    console.log(
      "Successfully copied node-definitions.json to vellum-ai package"
    );
  } catch (error) {
    console.error("Error copying node-definitions.json:", error);
  }
};

main();
