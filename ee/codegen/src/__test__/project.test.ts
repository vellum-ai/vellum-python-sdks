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
import { NodeAttributeGenerationError } from "src/generators/errors";
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
      faa_q_and_a_bot: SpyMocks.createWorkflowDeploymentsMock(),
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
          "simple_merge_node",
          "simple_api_node",
          "simple_node_with_try_wrap",
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
          options: {
            codeExecutionNodeCodeRepresentationOverride: "STANDALONE",
          },
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
  describe("failure cases", () => {
    const displayData = {
      workflow_raw_data: {
        nodes: [
          {
            id: "entry",
            type: "ENTRYPOINT",
            data: {
              label: "Entrypoint",
              source_handle_id: "entry_source",
              target_handle_id: "entry_target",
            },
            inputs: [],
          },
          {
            id: "bad_node",
            type: "TEMPLATING",
            data: {
              label: "Bad Node",
              template_node_input_id: "template",
              output_id: "output",
              output_type: "STRING",
              source_handle_id: "template_source",
              target_handle_id: "template_target",
            },
            inputs: [
              {
                id: "template",
                key: "template",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "foo",
                      },
                    },
                  ],
                },
              },
              {
                id: "input",
                key: "other",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "NODE_OUTPUT",
                      data: {
                        node_id: "node_that_doesnt_exist",
                        output_id: "output",
                      },
                    },
                  ],
                },
              },
            ],
          },
        ],
        edges: [
          {
            source_node_id: "entry",
            source_handle_id: "entry_source",
            target_node_id: "bad_node",
            target_handle_id: "template_target",
            type: "DEFAULT",
            id: "edge_1",
          },
        ],
      },
      input_variables: [],
      output_variables: [],
    };

    it("should generate code even if a node fails to generate", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      expect(
        fs.existsSync(join(tempDir, project.getModuleName(), "workflow.py"))
      ).toBe(true);
      expect(
        fs.existsSync(join(tempDir, project.getModuleName(), "nodes"))
      ).toBe(true);

      const badNodePath = join(
        tempDir,
        project.getModuleName(),
        "nodes",
        "bad_node.py"
      );
      expect(fs.existsSync(badNodePath)).toBe(true);
      expect(fs.readFileSync(badNodePath, "utf-8")).toBe(`\
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState


class BadNode(TemplatingNode[BaseState, str]):
    template = """foo"""
    inputs = {}
`);

      const errorLogPath = join(tempDir, project.getModuleName(), "error.log");
      expect(fs.existsSync(errorLogPath)).toBe(true);
      expect(fs.readFileSync(errorLogPath, "utf-8")).toBe(`\
Encountered 1 error(s) while generating code:

- Failed to generate attribute 'BadNode.inputs.other': Failed to find node with id 'node_that_doesnt_exist'
`);
    });

    it("should fail to generate code if a node fails in strict mode", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        strict: true,
      });

      expect(project.generateCode()).rejects.toThrow(
        new NodeAttributeGenerationError(
          "Failed to generate attribute 'BadNode.inputs.other': Failed to find node with id 'node_that_doesnt_exist'"
        )
      );
    });
  });
  describe("inlude sandbox", () => {
    const displayData = {
      workflow_raw_data: {
        nodes: [
          {
            id: "entry",
            type: "ENTRYPOINT",
            data: {
              label: "Entrypoint",
              source_handle_id: "entry_source",
              target_handle_id: "entry_target",
            },
            inputs: [],
          },
          {
            id: "templating-node",
            type: "TEMPLATING",
            data: {
              label: "Templating Node",
              template_node_input_id: "template",
              output_id: "output",
              output_type: "STRING",
              source_handle_id: "template_source",
              target_handle_id: "template_target",
            },
            inputs: [
              {
                id: "template",
                key: "template",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "{{input}}",
                      },
                    },
                  ],
                },
              },
              {
                id: "input",
                key: "other",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "INPUT_VARIABLE",
                      data: {
                        input_variable_id: "workflow-input",
                      },
                    },
                  ],
                },
              },
            ],
          },
        ],
        edges: [
          {
            source_node_id: "entry",
            source_handle_id: "entry_source",
            target_node_id: "templating-node",
            target_handle_id: "template_target",
            type: "DEFAULT",
            id: "edge_1",
          },
        ],
      },
      input_variables: [
        {
          key: "input",
          type: "STRING",
          id: "workflow-input",
        },
        {
          key: "chat",
          type: "CHAT_HISTORY",
          id: "workflow-chat",
        },
      ],
      output_variables: [],
    };
    it("should include a sandbox.py file when passed sandboxInputs", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        sandboxInputs: [
          [
            {
              name: "input",
              type: "STRING",
              value: "foo",
            },
            {
              name: "chat",
              type: "CHAT_HISTORY",
              value: [
                {
                  role: "USER",
                  text: "foo",
                },
              ],
            },
          ],
          [
            {
              name: "input",
              type: "STRING",
              value: "bar",
            },
            {
              name: "chat",
              type: "CHAT_HISTORY",
              value: [
                {
                  role: "USER",
                  content: {
                    type: "STRING",
                    value: "bar",
                  },
                  // The API sometimes sends null for source, but it's not a valid value
                  source: null as unknown as undefined,
                },
              ],
            },
          ],
          [
            {
              name: "input",
              type: "STRING",
              value: "hello",
            },
            {
              name: "chat",
              type: "CHAT_HISTORY",
              value: [
                {
                  role: "USER",
                  content: {
                    type: "ARRAY",
                    value: [
                      {
                        type: "STRING",
                        value: "hello",
                      },
                    ],
                  },
                },
              ],
            },
          ],
        ],
      });

      await project.generateCode();

      const sandboxPath = join(tempDir, project.getModuleName(), "sandbox.py");
      expect(fs.existsSync(sandboxPath)).toBe(true);
      expect(fs.readFileSync(sandboxPath, "utf-8")).toMatchSnapshot();
    });
  });
});
