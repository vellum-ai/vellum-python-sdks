import packageJson from "../package.json" assert { type: "json" };
import { getGithubToken } from "./get-github-token.mjs";
import { Octokit } from "@octokit/rest";

/*
 * This triggers the workflow server version release and lives here for convenience
 * so it can take advantage of the existing github app auth token.
 */
const main = async () => {
  const version = packageJson.version;
  console.log("Upgrading workflow server to version", version);
  const octokit = new Octokit({ auth: await getGithubToken() });
  await octokit.actions.createWorkflowDispatch({
    owner: "vellum-ai",
    repo: "vembda-service",
    workflow_id: "version-python-workflow-server.yaml",
    ref: "main",
    inputs: {
      version,
    },
  });

  console.log(
    "Successfully triggered workflow server github workflow, version:",
    version
  );
  process.exit(0);
};

main();
