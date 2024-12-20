import { createAppAuth } from "@octokit/auth-app";
import path from "path";
import os from "os";
import { execSync } from "child_process";
import packageJson from "../package.json" assert { type: "json" };

const getGithubToken = async () => {
  const appId = process.env.VELLUM_AUTOMATION_APP_ID;
  const privateKey = process.env.VELLUM_AUTOMATION_PRIVATE_KEY;
  const installationId = process.env.VELLUM_AUTOMATION_INSTALLATION_ID;

  if (!appId || !privateKey || !installationId) {
    throw new Error(
      "VELLUM_AUTOMATION_APP_ID, VELLUM_AUTOMATION_PRIVATE_KEY, and VELLUM_AUTOMATION_INSTALLATION_ID must be set"
    );
  }

  const auth = createAppAuth({
    appId,
    privateKey,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return token;
};

const main = async () => {
  const version = packageJson.version;
  console.log("Upgrading codegen service to version", version);

  const githubToken = await getGithubToken();
  const targetDir = path.join(os.tmpdir(), `codegen-service-${version}`);

  const repoUrl = `https://x-access-token:${githubToken}@github.com/vellum-ai/codegen-service.git`;
  execSync(`git clone ${repoUrl} ${targetDir}`, { stdio: "inherit" });

  process.chdir(targetDir);
  execSync(`npm run gar-login`, { stdio: "inherit" });
  execSync(`npm install @vellum-ai/vellum-codegen@${version} --save-exact`, {
    stdio: "inherit",
  });
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
