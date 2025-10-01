import fs from "fs";
import os from "os";
import path, { join } from "path";

import { WorkflowProjectGenerator } from "src/project";
import { getAllFilesInDir } from "src/utils/files";

const moduleName = "testing";
const vellumApiKey = "<TEST_API_KEY>";
const fixturesDir = path.join(__dirname, "generate-code-fixtures");

describe("generateCode", () => {
  const fixtures = fs
    .readdirSync(fixturesDir, { withFileTypes: true })
    .filter((file) => !file.isDirectory() && file.name.endsWith(".json"))
    .map((file) => file.name);

  it.each(fixtures)(`should generate code for %1`, async (fixture) => {
    const { assertions, ...workflowVersionExecConfigData } = JSON.parse(
      fs.readFileSync(path.join(fixturesDir, fixture), "utf8")
    );

    const tempDir = path.join(
      os.tmpdir(),
      "generate-code",
      fixture.replace(".json", "")
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
