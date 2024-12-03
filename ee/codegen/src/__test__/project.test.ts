import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { difference } from "lodash";
import { expect } from "vitest";

import {
  getAllFilesInDir,
  getFixturesForProjectTest,
} from "./helpers/fixtures";
import { makeTempDir } from "./helpers/temp-dir";

import { SpyMocks } from "src/__test__/utils/SpyMocks";
import { WorkflowProjectGenerator } from "src/project";

describe("WorkflowProjectGenerator", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = makeTempDir("project-test");
    await mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true });
  });

  describe("generateCode", () => {
    const excludeFilesAtPaths: RegExp[] = [/\.pyc$/];
    const ignoreContentsOfFilesAtPaths: RegExp[] = [];
    const fixtureMocks = {
      simple_guard_rail_node: SpyMocks.createMetricDefinitionMock(),
    };

    it.each(
      getFixturesForProjectTest({
        includeFixtures: [
          "simple_search_node",
          "simple_inline_subworkflow_node",
          "simple_guardrail_node",
          "simple_prompt_node",
          "simple_map_node",
          "simple_code_execution_node",
          "simple_conditional_node",
          "simple_templating_node",
          "simple_error_node",
          // TODO: Get Merge Node graph codegen working
          //    https://app.shortcut.com/vellum/story/5588
          // "simple_merge_node",
        ],
        fixtureMocks: fixtureMocks,
      })
    )(
      "should correctly generate code for fixture $fixtureName",
      async ({ displayFile, codeDir }) => {
        const displayData: unknown = JSON.parse(
          fs.readFileSync(displayFile, "utf-8")
        );

        const project = new WorkflowProjectGenerator({
          absolutePathToOutputDirectory: tempDir,
          workflowVersionExecConfigData: displayData,
          moduleName: "code",
          vellumApiKey: "<TEST_API_KEY>",
        });

        await project.generateCode();

        const generatedFiles = getAllFilesInDir(
          join(tempDir, project.getModuleName())
        );
        const expectedFiles = getAllFilesInDir(codeDir, excludeFilesAtPaths);

        const extraFilePaths = difference(
          Object.keys(generatedFiles),
          Object.keys(expectedFiles)
        );
        const extraFiles = extraFilePaths.map((path) => generatedFiles[path]);
        expect(extraFiles.length, `Found extra file(s): ${extraFiles}`).toBe(0);

        for (const [
          expectedRelativePath,
          expectedAbsolutePath,
        ] of Object.entries(expectedFiles)) {
          const generatedAbsolutePath = generatedFiles[expectedRelativePath];

          if (!generatedAbsolutePath) {
            throw new Error(
              `Expected to have generated a file at the path: ${expectedRelativePath}`
            );
          }

          if (
            ignoreContentsOfFilesAtPaths.some((regex) =>
              regex.test(expectedRelativePath)
            )
          ) {
            continue;
          }

          const generatedFileContents = fs.readFileSync(
            generatedAbsolutePath,
            "utf-8"
          );

          expect(generatedFileContents).toMatchFileSnapshot(
            expectedAbsolutePath,
            `File contents don't match snapshot: ${expectedRelativePath}`
          );
        }
      }
    );
  });
});
