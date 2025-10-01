import fs from "fs";
import os from "os";
import path, { join } from "path";

import { WorkflowProjectGenerator } from "src/project";
import { getAllFilesInDir } from "src/utils/files";

const moduleName = "testing";
const vellumApiKey = "<TEST_API_KEY>";
const fixturesDir = path.join(__dirname, "generate-code-fixtures");

/**
 * New pattern for testing project level codegen features and to start reducing the size of `projecte.test.ts`.
 * - Create a new file within `__test__/generate-code-fixtures`
 * - The file should export a default object with the following properties:
 *   - assertions: an array of file paths to assert snapshots against
 *   - workflow_raw_data: the raw workflow data to pass to the `WorkflowProjectGenerator`
 *   - The rest of workflow version exec config data also top level.
 */
describe("generateCode", () => {
  let tempDir: string;
  beforeAll(() => {
    tempDir = path.join(os.tmpdir(), "generate-code");
    fs.mkdirSync(tempDir, { recursive: true });
  });

  afterAll(() => {
    fs.rmSync(tempDir, { recursive: true });
  });

  const fixtures = fs
    .readdirSync(fixturesDir, { withFileTypes: true })
    .filter((file) => !file.isDirectory() && file.name.endsWith(".ts"))
    .map((file) => file.name);

  it.each(fixtures)(`should generate code for %1`, async (fixture) => {
    const fixtureModule = await import(path.join(fixturesDir, fixture));
    const { assertions, ...workflowVersionExecConfigData } =
      fixtureModule.default;

    const fixtureDir = path.join(tempDir, fixture.replace(/\.ts$/, ""));
    fs.mkdirSync(fixtureDir, { recursive: true });

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
