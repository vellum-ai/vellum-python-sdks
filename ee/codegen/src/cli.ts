import { readFile } from "fs/promises";
import * as path from "path";

import { WorkflowProjectGenerator } from "./project";

interface CliArgs {
  execConfigPath: string;
  outputDir: string;
  moduleName: string;
  originalArtifactPath?: string;
}

function parseArgs(argv: string[]): CliArgs {
  const args: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    if (!key) continue;
    if (!key.startsWith("--")) continue;
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${key}`);
    }
    const normalized = key.slice(2);
    args[normalized] = value;
    i++;
  }

  const execConfigPath = args["exec-config"];
  const outputDir = args["output-dir"];
  const moduleName = args["module-name"];
  const originalArtifactPath = args["original-artifact"];

  if (!execConfigPath || !outputDir || !moduleName) {
    throw new Error(
      "Usage: cli.ts --exec-config <path> --output-dir <dir> --module-name <module> [--original-artifact <path>]"
    );
  }

  return {
    execConfigPath,
    outputDir,
    moduleName,
    originalArtifactPath,
  };
}

async function main() {
  try {
    const { execConfigPath, outputDir, moduleName, originalArtifactPath } =
      parseArgs(process.argv.slice(2));

    const execConfigRaw = await readFile(execConfigPath, "utf-8");
    const execConfig = JSON.parse(execConfigRaw);

    const generator = new WorkflowProjectGenerator({
      moduleName,
      absolutePathToOutputDirectory: path.resolve(outputDir),
      workflowVersionExecConfigData: execConfig,
      strict: false,
    });

    let originalArtifact: Record<string, string> | undefined;
    if (originalArtifactPath) {
      const artifactRaw = await readFile(originalArtifactPath, "utf-8");
      originalArtifact = JSON.parse(artifactRaw);
    }

    await generator.generateCode(originalArtifact);

    process.exit(0);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
}

void main();
