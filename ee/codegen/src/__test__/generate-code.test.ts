import fs from "fs";
import os from "os";
import path, { join } from "path";

import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors/VellumError";
import { vi } from "vitest";

import { WorkflowProjectGenerator } from "src/project";
import { getAllFilesInDir } from "src/utils/files";

const moduleName = "testing";
const vellumApiKey = "<TEST_API_KEY>";
const fixturesDir = path.join(__dirname, "generate-code-fixtures");

describe("generateCode", () => {
  beforeEach(() => {
    vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockRejectedValue(
      new VellumError({
        message: "Workspace secret not found",
        statusCode: 404,
      })
    );
  });

  const fixtures = fs
    .readdirSync(fixturesDir, { withFileTypes: true })
    .filter(
      (file) =>
        !file.isDirectory() &&
        (file.name.endsWith(".json") || file.name.endsWith(".ts"))
    )
    .map((file) => file.name);

  it.each(fixtures)(`should generate code for %1`, async (fixture) => {
    let workflowVersionExecConfigData: any;
    let assertions: string[];

    if (fixture.endsWith(".json")) {
      const fixtureData = JSON.parse(
        fs.readFileSync(path.join(fixturesDir, fixture), "utf8")
      );
      assertions = fixtureData.assertions;
      workflowVersionExecConfigData = {
        ...fixtureData,
        assertions: undefined,
      };
      delete workflowVersionExecConfigData.assertions;
    } else if (fixture.endsWith(".ts")) {
      const fixtureModule = require(path.join(fixturesDir, fixture));
      const fixtureData = fixtureModule.default;
      assertions = fixtureData.assertions;
      workflowVersionExecConfigData = {
        ...fixtureData,
        assertions: undefined,
      };
      delete workflowVersionExecConfigData.assertions;
    } else {
      throw new Error(`Unsupported fixture format: ${fixture}`);
    }

    const tempDir = path.join(
      os.tmpdir(),
      "generate-code",
      fixture.replace(/\.(json|ts)$/, "")
    );
    fs.mkdirSync(tempDir, { recursive: true });

    async function expectProjectFileToMatchSnapshot(filePath: string[]) {
      const moduleRoot = join(tempDir, moduleName);
      const completeFilePath = join(moduleRoot, ...filePath);
      const snapshotName = filePath.join("/");
      expect(
        fs.existsSync(completeFilePath),
        `File does not exist: ${snapshotName}. Files generated:\n${Object.keys(
          await getAllFilesInDir(moduleRoot)
        ).join("\n")}`
      ).toBe(true);
      expect(fs.readFileSync(completeFilePath, "utf-8")).toMatchSnapshot(
        snapshotName
      );
    }

    const project = new WorkflowProjectGenerator({
      absolutePathToOutputDirectory: tempDir,
      workflowVersionExecConfigData,
      moduleName,
      vellumApiKey,
    });
    await project.generateCode();

    for (const assertion of assertions) {
      await expectProjectFileToMatchSnapshot([assertion]);
    }
  });
});
