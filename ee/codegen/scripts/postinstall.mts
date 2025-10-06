import { existsSync, copyFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const main = async () => {
  try {
    const initCwd = process.env.INIT_CWD;
    const packageRoot = path.resolve(__dirname, "..");

    if (initCwd && path.resolve(initCwd) !== packageRoot) {
      console.log(
        "Skipping postinstall copy - package is being installed as a dependency"
      );
      return;
    }

    const sourceFile = path.join(
      __dirname,
      "..",
      "..",
      "vellum_ee",
      "assets",
      "node-definitions.json"
    );
    const targetDir = path.join(__dirname, "..", "src", "assets");
    const targetFile = path.join(targetDir, "node-definitions.json");

    if (!existsSync(sourceFile)) {
      console.log("Source file does not exist, skipping postinstall copy");
      return;
    }

    copyFileSync(sourceFile, targetFile);
    console.log("Successfully copied node-definitions.json to src/assets");
  } catch (error) {
    console.error("Error in postinstall script:", error);
  }
};

main();
