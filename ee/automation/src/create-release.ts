import fs from "fs";
import path from "path";
import { Octokit } from "@octokit/rest";
import { getGithubToken } from "./auth.js";
import { fileURLToPath } from "url";
import dotenv from "dotenv";

dotenv.config();

const SDK_REPO = "vellum-python-sdks";

const main = async () => {
  // Read and parse pyproject.toml
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const pyprojectToml = fs.readFileSync(
    path.join(__dirname, "..", "..", "..", "pyproject.toml"),
    "utf8"
  );

  // Extract version from pyproject.toml using regex
  const version = pyprojectToml.match(/version = "([^"]+)"/)?.[1];
  if (!version) {
    throw new Error("Could not find version in pyproject.toml");
  }
  console.log("Found Version:", version);

  // Create the release
  const auth = await getGithubToken();
  const octokit = new Octokit({
    auth,
  });

  const sdkReleases = await octokit.rest.repos.listReleases({
    owner: "vellum-ai",
    repo: SDK_REPO,
  });
  if (sdkReleases.data.find((release) => release.name === version)) {
    throw new Error(`Release '${version}' already exists in '${SDK_REPO}'`);
  }

  const generatorReleases = await octokit.rest.repos.listReleases({
    owner: "vellum-ai",
    repo: "vellum-client-generator",
  });
  const targetedRelease = generatorReleases.data.find(
    (release) => release.name === version
  );
  if (!targetedRelease?.body) {
    throw new Error(
      `Release '${version}' does not exist in 'vellum-client-generator'`
    );
  }

  await octokit.rest.repos.createRelease({
    owner: "vellum-ai",
    repo: SDK_REPO,
    tag_name: version,
    make_latest: "true",
    name: version,
    body: targetedRelease.body,
  });

  console.log(`Successfully created release '${version}'`);
};

main();
