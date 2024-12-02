import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { difference } from "lodash";
import { WorkflowDeploymentHistoryItem } from "vellum-ai/api";
import {
  WorkflowDeployments,
  WorkflowDeployments as WorkflowDeploymentsClient,
} from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { expect, vi } from "vitest";

import {
  getAllFilesInDir,
  getFixturesForProjectTest,
} from "./helpers/fixtures";
import { makeTempDir } from "./helpers/temp-dir";

import { WorkflowProjectGenerator } from "src/project";

interface MockReturnValue {
  workflowDeploymentHistoryItemRetrieve?: Awaited<
    ReturnType<WorkflowDeployments["workflowDeploymentHistoryItemRetrieve"]>
  >;
}

const MOCK_RETURN_VALUES_BY_FIXTURE_NAME: Readonly<
  Record<string, MockReturnValue>
> = {
  faa_q_and_a_bot: {
    workflowDeploymentHistoryItemRetrieve: {
      name: "test-deployment",
      outputVariables: [
        {
          id: "53970e88-0bf6-4364-86b3-840d78a2afe5",
          key: "chat_history",
          type: "CHAT_HISTORY",
        },
      ],
    } as unknown as WorkflowDeploymentHistoryItem,
  },
};

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

    it.each(
      getFixturesForProjectTest({
        includeFixtures: [
          "simple_search_node",
          // TODO: Fix codegen for inline subworkflow node
          // https://app.shortcut.com/vellum/story/5662/fix-codegen-for-inline-subworkflow-node
          // "simple_inline_subworkflow_node",
          // TODO: Fix codegen for guardrail node
          // https://app.shortcut.com/vellum/story/5663/fix-codegen-of-guardrail-nodes
          // "simple_guardrail_node",
          "simple_prompt_node",
          // TODO: Fix codegen for map node
          // https://app.shortcut.com/vellum/story/5666/fix-codegen-for-map-node
          //"simple_map_node",
          "simple_code_execution_node",
          "simple_conditional_node",
          "simple_templating_node",
          "faa_q_and_a_bot",
        ],
      })
    )(
      "should correctly generate code for fixture $fixtureName",
      async ({ displayFile, codeDir, fixtureName }) => {
        if (
          MOCK_RETURN_VALUES_BY_FIXTURE_NAME[fixtureName]?.[
            "workflowDeploymentHistoryItemRetrieve"
          ]
        ) {
          vi.spyOn(
            WorkflowDeploymentsClient.prototype,
            "workflowDeploymentHistoryItemRetrieve"
          ).mockResolvedValue(
            MOCK_RETURN_VALUES_BY_FIXTURE_NAME[fixtureName][
              "workflowDeploymentHistoryItemRetrieve"
            ]
          );
        }

        const displayData: unknown = JSON.parse(
          fs.readFileSync(displayFile, "utf-8")
        );

        const project = new WorkflowProjectGenerator({
          absolutePathToOutputDirectory: tempDir,
          workflowLabel: "Workflow",
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
