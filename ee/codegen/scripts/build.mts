import { execSync } from "child_process";
import { existsSync, mkdirSync, copyFileSync, readdirSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const main = () => {
  execSync("tsc && tsc-alias", { stdio: "inherit" });

  const srcAssetsDir = path.join(__dirname, "..", "src", "assets");
  const libAssetsDir = path.join(__dirname, "..", "lib", "src", "assets");

  mkdirSync(libAssetsDir, { recursive: true });

  if (existsSync(srcAssetsDir)) {
    const files = readdirSync(srcAssetsDir);
    files
      .filter((file) => file.endsWith(".json"))
      .forEach((file) => {
        const srcFile = path.join(srcAssetsDir, file);
        const destFile = path.join(libAssetsDir, file);
        copyFileSync(srcFile, destFile);
      });
  }
};

main();
