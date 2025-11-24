import path from "path";
import os from "os";
import { execSync } from "child_process";
import packageJson from "../package.json" assert { type: "json" };
import { readFileSync, writeFileSync } from "node:fs";
import { getGithubToken } from "./get-github-token.mjs";
import dotenv from "dotenv";

dotenv.config();

const main = async () => {
  const version = packageJson.version;
  console.log("Upgrading codegen service to version", version);

  const targetDir = path.join(os.tmpdir(), `codegen-service-${version}`);

  if (process.env.LOCAL_DEV) {
    const repoUrl = `git@github.com:vellum-ai/codegen-service.git`;
    execSync(`git clone ${repoUrl} ${targetDir}`, { stdio: "inherit" });
  } else {
    const githubToken = await getGithubToken();
    const repoUrl = `https://x-access-token:${githubToken}@github.com/vellum-ai/codegen-service.git`;
    execSync(`git clone ${repoUrl} ${targetDir}`, { stdio: "inherit" });
  }

  process.chdir(targetDir);
  execSync(`npm install -g pnpm`, { stdio: "inherit" });
  execSync(`npm run gar-login`, { stdio: "inherit" });
  execSync(`pnpm install @vellum-ai/vellum-codegen@${version} --save-exact`, {
    stdio: "inherit",
  });
  execSync(
    `pnpm install @vellum-ai/vellum-codegen-${version}@npm:@vellum-ai/vellum-codegen@${version}  --save-exact`,
    {
      stdio: "inherit",
    }
  );
  execSync(`pnpm run postinstall`, { stdio: "inherit" });

  // Generate our codegen module lookup function. If we generate all if cases instead of
  // passing in a variable version to the async imports this will cause static type checking
  // which will at least somewhat cover our bases with version interface changes until we have
  // e2e tests of codegen service.
  const codegenPackageJson = JSON.parse(
    readFileSync(path.join(targetDir, "package.json"), "utf8")
  );

  const packageVersionsLookups = Object.keys(codegenPackageJson.dependencies)
    .filter((dep) => dep.startsWith("@vellum-ai/vellum-codegen-"))
    .map((dep) => {
      const version = dep.replace("@vellum-ai/vellum-codegen-", "");
      return `  if (version === "${version}") {
    return import("@vellum-ai/vellum-codegen-${version}/lib/src");
  }`;
    })
    .join("\n");

  const codeGeneratorFunction = `// @ts-nocheck
/**
 * This file was generated automatically by the codegen CD pipeline in vellum-python-sdks do not modify it.
 *
 * We don't have type declarations for older vellum-codegen versions, so we need to ts-ignore the whole file.
 **/
export const getCodegenModule = async (version: string | null | undefined) => {
${packageVersionsLookups}

  return null;
};
`;
  writeFileSync(
    path.join(targetDir, "src/utils/getCodegenModule.ts"),
    codeGeneratorFunction
  );
  execSync(`pnpm run types`, { stdio: "inherit" });
  execSync(`pnpm run lint:fix`, { stdio: "inherit" });

  execSync('git config user.name "vellum-automation[bot]"', {
    stdio: "inherit",
  });
  execSync(
    'git config user.email "vellum-automation[bot]@users.noreply.github.com"',
    { stdio: "inherit" }
  );
  execSync(`git add --all`, { stdio: "inherit" });
  execSync(`git commit -m "Upgrade codegen service to ${version}"`, {
    stdio: "inherit",
  });
  execSync(`git push origin main`, { stdio: "inherit" });
  console.log("Successfully pushed", version, "to main!");
  process.exit(0);
};

main();
