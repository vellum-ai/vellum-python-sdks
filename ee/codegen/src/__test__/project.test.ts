import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { difference } from "lodash";
import { v4 as uuidv4 } from "uuid";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { expect, vi } from "vitest";

import {
  getAllFilesInDir,
  getFixturesForProjectTest,
} from "./helpers/fixtures";
import { makeTempDir } from "./helpers/temp-dir";

import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { SpyMocks } from "src/__test__/utils/SpyMocks";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { WorkflowProjectGenerator } from "src/project";

describe("WorkflowProjectGenerator", () => {
  let tempDir: string;

  function expectProjectFileToMatchSnapshot(filePath: string[]) {
    const completeFilePath = join(tempDir, ...filePath);
    expect(
      fs.existsSync(completeFilePath),
      `File does not exist: ${completeFilePath}. Files generated:\n${Object.keys(
        getAllFilesInDir(join(tempDir))
      ).join("\n")}`
    ).toBe(true);
    expect(fs.readFileSync(completeFilePath, "utf-8")).toMatchSnapshot();
  }

  function expectProjectFileToExist(filePath: string[]) {
    const completeFilePath = join(tempDir, ...filePath);

    expect(
      fs.existsSync(completeFilePath),
      `File does not exist: ${completeFilePath}. Files generated:\n${Object.keys(
        getAllFilesInDir(join(tempDir))
      ).join("\n")}`
    ).toBe(true);
  }

  function expectErrorLog(filePath: string[], expectedContents: string = "") {
    const errorLogPath = join(tempDir, ...filePath, "error.log");
    const errorLog = fs.existsSync(errorLogPath)
      ? fs.readFileSync(errorLogPath, "utf-8")
      : "";
    expect(errorLog).toBe(expectedContents);
  }

  beforeEach(async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );

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
      simple_subworkflow_deployment_node:
        SpyMocks.createWorkflowDeploymentsMock(),
    };
    vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockImplementation(
      // @ts-ignore
      async (idOrName: string) => {
        return {
          id: idOrName,
          name: "TEST_SECRET",
          modified: new Date(),
          label: idOrName,
          secretType: "USER_DEFINED",
        };
      }
    );

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
          "simple_subworkflow_deployment_node",
          "simple_workflow_node_with_output_values",
          "faa_q_and_a_bot",
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
          strict: true,
        });

        await project.generateCode();

        const generatedFiles = getAllFilesInDir(
          join(tempDir, ...project.getModulePath())
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
    let displayData = {
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
      state_variables: [],
      output_variables: [],
    };

    it("should generate code even if a node fails to generate", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "bad_node.py"]);

      const errors = project.workflowContext.getErrors();
      expect(errors.length).toBe(1);
      expect(errors[0]?.message).toBe(
        "Failed to find node with id 'node_that_doesnt_exist'"
      );
      expect(errors[0]?.severity).toBe("WARNING");
    });

    it("should fail to generate code if a node fails in strict mode", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
        strict: true,
      });

      expect(project.generateCode()).rejects.toThrow(
        new NodeAttributeGenerationError(
          "Failed to generate attribute 'BadNode.inputs.other': Failed to find node with id 'node_that_doesnt_exist'"
        )
      );
    });

    it("should generate code even if a node fails to find invalid ports and target nodes", async () => {
      displayData = {
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
              id: "some-node-id",
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
              ],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry-source",
              target_node_id: "some-node-id",
              target_handle_id: "template_target",
              type: "DEFAULT",
              id: "edge_1",
            },
            {
              source_node_id: "bad-source-node-id",
              source_handle_id: "bad-source-handle-id",
              target_node_id: "bad-target",
              target_handle_id: "template_target",
              type: "DEFAULT",
              id: "edge_1",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "bad_node.py"]);
    });
  });
  describe("include sandbox", () => {
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
      state_variables: [],
      output_variables: [],
    };
    it("should include a sandbox.py file when passed sandboxInputs", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
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

      expectProjectFileToMatchSnapshot(["code", "sandbox.py"]);
    });
  });
  describe("runner config with no container image", () => {
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
                        value: "hello",
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
      input_variables: [],
      state_variables: [],
      output_variables: [],
      runner_config: {},
    };
    it("should handle a runner config with no container image", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot(["code", "workflow.py"]);
    });
  });

  describe("multiple nodes with the same label", () => {
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
                        value: "hello",
                      },
                    },
                  ],
                },
              },
            ],
          },
          {
            id: "templating-node-1",
            type: "TEMPLATING",
            data: {
              label: "Templating Node",
              template_node_input_id: "template",
              output_id: "output",
              output_type: "STRING",
              source_handle_id: "template_source_1",
              target_handle_id: "template_target_1",
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
                        value: "world",
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
          {
            source_node_id: "templating-node",
            source_handle_id: "template_source",
            target_node_id: "templating-node-1",
            target_handle_id: "template_target_1",
            type: "DEFAULT",
            id: "edge_2",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [],
      runner_config: {},
    };
    it("should handle the case of multiple nodes with the same label", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToExist(["code", "nodes", "templating_node_1.py"]);
    });
  });

  describe("code execution node at project level", () => {
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
            id: "code-node",
            type: "CODE_EXECUTION",
            data: {
              label: "Code Execution Node",
              code_input_id: "code",
              runtime_input_id: "python",
              output_id: "output",
              output_type: "STRING",
              source_handle_id: "code_source",
              target_handle_id: "code_target",
            },
            inputs: [
              {
                id: "code",
                key: "code",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: `\
import foo, bar
baz = foo + bar
`,
                      },
                    },
                  ],
                },
              },
              {
                id: "python",
                key: "runtime",
                value: {
                  combinator: "OR",
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "PYTHON_3_11_6",
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
            target_node_id: "code-node",
            target_handle_id: "code_target",
            type: "DEFAULT",
            id: "edge_1",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [],
      runner_config: {},
    };
    it("should not autoformat the script file", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
        strict: true,
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "code_execution_node",
        "script.py",
      ]);
    });
  });

  describe("Nodes with forward references", () => {
    const firstNodeId = uuidv4();
    const secondNodeId = uuidv4();
    const secondNodeOutputId = uuidv4();
    const firstNodeDefaultPortId = uuidv4();
    const firstNodeTriggerId = uuidv4();
    const secondNodeTriggerId = uuidv4();
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
            id: firstNodeId,
            type: "GENERIC",
            label: "First Node",
            attributes: [
              {
                id: uuidv4(),
                name: "forward",
                value: {
                  type: "NODE_OUTPUT",
                  node_id: secondNodeId,
                  node_output_id: secondNodeOutputId,
                },
              },
            ],
            trigger: {
              id: firstNodeTriggerId,
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            ports: [
              {
                id: firstNodeDefaultPortId,
                name: "default",
                type: "DEFAULT",
              },
            ],
            base: {
              name: "BaseNode",
              module: ["vellum", "workflows", "nodes", "bases", "base"],
            },
            outputs: [],
          },
          {
            id: secondNodeId,
            type: "GENERIC",
            label: "Second Node",
            attributes: [],
            outputs: [
              {
                id: secondNodeOutputId,
                name: "output",
                type: "STRING",
              },
            ],
            ports: [],
            trigger: {
              id: secondNodeTriggerId,
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            base: {
              name: "BaseNode",
              module: ["vellum", "workflows", "nodes", "bases", "base"],
            },
          },
        ],
        edges: [
          {
            source_node_id: "entry",
            source_handle_id: "entry_source",
            target_node_id: firstNodeId,
            target_handle_id: firstNodeTriggerId,
            type: "DEFAULT",
            id: "edge_1",
          },
          {
            source_node_id: firstNodeId,
            source_handle_id: firstNodeDefaultPortId,
            target_node_id: secondNodeId,
            target_handle_id: secondNodeTriggerId,
            type: "DEFAULT",
            id: "edge_2",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [],
      runner_config: {},
    };
    it("should generate a proper Lazy Reference for the first node", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
        strict: false,
      });

      await project.generateCode();

      expectErrorLog(["code"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "first_node.py"]);
    });
  });

  // TODO: Remove this once we move away completely from terminal nodes
  describe("nodes with output values", () => {
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
                        value: "hello",
                      },
                    },
                  ],
                },
              },
            ],
          },
          {
            id: "terminal-node",
            type: "TERMINAL",
            data: {
              label: "Final Output",
              name: "final-output",
              target_handle_id: "terminal_target",
              output_id: "terminal_output_id",
              output_type: "STRING",
              node_input_id: "terminal_input",
            },
            inputs: [
              {
                id: "terminal_input",
                key: "node_input",
                value: {
                  rules: [
                    {
                      type: "NODE_OUTPUT",
                      data: {
                        node_id: "templating-node",
                        output_id: "output",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
            ],
            outputs: [
              {
                id: "some-id",
                name: "node_input",
                type: "STRING",
                value: {
                  type: "NODE_OUTPUT",
                  node_id: "templating-node",
                  node_output_id: "output",
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
          {
            source_node_id: "templating-node",
            source_handle_id: "template_source",
            target_node_id: "terminal-node",
            target_handle_id: "terminal_target",
            type: "DEFAULT",
            id: "edge_2",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [
        {
          id: "not-used-output-variable-id",
          key: "not-used-output-variable-key",
          type: "STRING",
        },
      ],
      output_values: [
        {
          output_variable_id: "not-used-output-variable-id",
          value: {
            type: "NODE_OUTPUT",
            node_id: "not-used-node-id",
            node_output_id: "not-used-node-output-id",
          },
        },
      ],
      runner_config: {},
    };
    it("should prioritize terminal node data over output values", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
        strict: true,
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "final_output.py"]);
    });
  });

  describe("Nodes present but not in graph", () => {
    const firstNodeId = uuidv4();
    const secondNodeId = uuidv4();
    const secondNodeOutputId = uuidv4();
    const firstNodeTriggerId = uuidv4();
    const secondNodeTriggerId = uuidv4();
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
            id: firstNodeId,
            type: "GENERIC",
            label: "First Node",
            attributes: [],
            trigger: {
              id: firstNodeTriggerId,
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            ports: [],
            base: {
              name: "BaseNode",
              module: ["vellum", "workflows", "nodes", "bases", "base"],
            },
            outputs: [],
          },
          {
            id: secondNodeId,
            type: "GENERIC",
            label: "Second Node",
            attributes: [],
            outputs: [
              {
                id: secondNodeOutputId,
                name: "output",
                type: "STRING",
              },
            ],
            ports: [],
            trigger: {
              id: secondNodeTriggerId,
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            base: {
              name: "BaseNode",
              module: ["vellum", "workflows", "nodes", "bases", "base"],
            },
          },
        ],
        edges: [
          {
            source_node_id: "entry",
            source_handle_id: "entry_source",
            target_node_id: firstNodeId,
            target_handle_id: firstNodeTriggerId,
            type: "DEFAULT",
            id: "edge_1",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [],
      runner_config: {},
    };
    it("should still generate a file for the second node", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
        strict: false,
      });

      await project.generateCode();

      // There should be no errors
      expectErrorLog(["code"]);

      // We should have generated a Workflow that has a graph containing only the first node
      expectProjectFileToMatchSnapshot(["code", "workflow.py"]);

      // We should have generated a file for the second node, even though it's not in the graph
      expectProjectFileToMatchSnapshot(["code", "nodes", "second_node.py"]);

      // We should have generated a display file for the second node
      expectProjectFileToMatchSnapshot([
        "code",
        "display",
        "nodes",
        "second_node.py",
      ]);

      // We should have included the second node in our init files
      expectProjectFileToMatchSnapshot(["code", "nodes", "__init__.py"]);
      expectProjectFileToMatchSnapshot([
        "code",
        "display",
        "nodes",
        "__init__.py",
      ]);
    });
    it("should generate unused_graphs if final output is not used", async () => {
      // GIVEN a workflow where final output is not used
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "edge_1",
              type: "DEFAULT",
              source_node_id: "entrypoint",
              target_node_id: "generic-node",
              source_handle_id: "entrypoint_source",
              target_handle_id: "generic-node-trigger",
            },
          ],
          nodes: [
            {
              id: "generic-node",
              type: "GENERIC",
              label: "Generic Node",
              attributes: [],
              trigger: {
                id: "generic-node-trigger",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: "generic-node-default-port",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              outputs: [],
            },
            {
              id: "entrypoint",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "e345568c-6f75-4aab-ab46-a189a069870f",
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
              display_data: {
                width: 124.0,
                height: 48.0,
                comment: null,
                position: { x: 1545.0, y: 330.0 },
              },
            },
            {
              id: "terminal",
              base: null,
              data: {
                name: "final-output",
                label: "Final Output",
                output_id: "terminal_output",
                output_type: "STRING",
                node_input_id: "terminal_input",
                target_handle_id: "terminal_target",
              },
              type: "TERMINAL",
              inputs: [
                {
                  id: "terminal_input",
                  key: "node_input",
                  value: { rules: [], combinator: "OR" },
                },
              ],
              trigger: {
                id: "terminal_target",
                merge_behavior: "AWAIT_ANY",
              },
              definition: null,
              display_data: {
                width: 454.0,
                height: 239.0,
                comment: null,
                position: { x: 2750.0, y: 210.0 },
              },
            },
          ],
          definition: null,
          display_data: {
            viewport: {
              x: -1120.031727765905,
              y: 146.58014137760972,
              zoom: 0.7660693736643104,
            },
          },
          output_values: [
            {
              value: {
                type: "NODE_OUTPUT",
                node_id: "generic-node",
                node_output_id: "output",
              },
              output_variable_id: "not-used-output-variable-id",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot(["code", "workflow.py"]);
    });
  });

  describe("initialization case", () => {
    it("should handle workflow with only ENTRYPOINT and TERMINAL nodes", async () => {
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
              id: "terminal-node",
              type: "TERMINAL",
              data: {
                label: "Final Output",
                name: "final-output",
                target_handle_id: "terminal_target",
                output_id: "terminal_output_id",
                output_type: "STRING",
                node_input_id: "terminal_input",
              },
              inputs: [
                {
                  id: "terminal_input",
                  key: "node_input",
                  value: {
                    rules: [],
                    combinator: "OR",
                  },
                },
              ],
            },
          ],
          edges: [],
        },
        input_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "final_output.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "final_output.py"]);
    });
  });
  describe("adornments", () => {
    it("should correctly generate code for a prompt node with retry adornment", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "6790c12c-a93e-4899-a63c-530d002c4c6f",
              type: "DEFAULT",
              source_node_id: "9bfb7aaf-d1b7-4fc1-9349-08f0dcc4c918",
              target_node_id: "82d5c288-aab8-4d27-bceb-4ba7bc688c34",
              source_handle_id: "b275fc98-4945-4e6d-bdb8-d9e9f4ca7444",
              target_handle_id: "0f3f518a-ce24-4355-8568-94e1bf295725",
            },
            {
              id: "39804f2f-ad65-471d-8d22-f37621164904",
              type: "DEFAULT",
              source_node_id: "82d5c288-aab8-4d27-bceb-4ba7bc688c34",
              target_node_id: "e0dfea1e-391d-4dee-9d71-28b391106726",
              source_handle_id: "c678ddd0-f646-4bd3-9557-9ad63f6d8f3c",
              target_handle_id: "fd2ee2c7-e9d8-42f4-9bc6-d22fe22a3044",
            },
          ],
          nodes: [
            {
              id: "9bfb7aaf-d1b7-4fc1-9349-08f0dcc4c918",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "b275fc98-4945-4e6d-bdb8-d9e9f4ca7444",
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
              display_data: {
                width: 124.0,
                height: 48.0,
                comment: null,
                position: { x: 1545.0, y: 330.0 },
              },
            },
            {
              id: "82d5c288-aab8-4d27-bceb-4ba7bc688c34",
              base: null,
              data: {
                label: "Prompt",
                variant: "INLINE",
                output_id: "e054f21d-33e1-4c76-8b1d-b22c393f6c7d",
                exec_config: {
                  settings: null,
                  parameters: {
                    stop: null,
                    top_k: 0,
                    top_p: 1.0,
                    logit_bias: {},
                    max_tokens: 1000,
                    temperature: 0.0,
                    presence_penalty: 0.0,
                    custom_parameters: null,
                    frequency_penalty: 0.0,
                  },
                  input_variables: [
                    {
                      id: "043a9f22-17c2-4d51-b106-753842a0c0b9",
                      key: "text",
                      type: "STRING",
                      default: null,
                      required: null,
                      extensions: null,
                    },
                  ],
                  prompt_template_block_data: {
                    blocks: [
                      {
                        id: "96af896b-f415-4ae4-aa80-cead3a7d068b",
                        state: "ENABLED",
                        block_type: "CHAT_MESSAGE",
                        properties: {
                          blocks: [
                            {
                              id: "02870e84-9ba5-4862-a68d-14b9f86d4100",
                              state: "ENABLED",
                              blocks: [
                                {
                                  id: "cab5064b-f52b-4398-8c95-155e70b37aac",
                                  text: "Summarize the following text: hello today is feb 7 bad weather\n\n",
                                  state: "ENABLED",
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
                                },
                                {
                                  id: "df088249-3ba0-47df-997e-e6f1f4e25feb",
                                  state: "ENABLED",
                                  block_type: "VARIABLE",
                                  cache_config: null,
                                  input_variable_id:
                                    "043a9f22-17c2-4d51-b106-753842a0c0b9",
                                },
                              ],
                              block_type: "RICH_TEXT",
                              cache_config: null,
                            },
                          ],
                          chat_role: "SYSTEM",
                          chat_source: null,
                          chat_message_unterminated: false,
                        },
                        cache_config: null,
                      },
                    ],
                    version: 1,
                  },
                },
                ml_model_name: "gpt-4o-mini",
                array_output_id: "191a66c6-3e38-45e0-b5dd-5e644fdec8b0",
                error_output_id: null,
                source_handle_id: "c678ddd0-f646-4bd3-9557-9ad63f6d8f3c",
                target_handle_id: "0f3f518a-ce24-4355-8568-94e1bf295725",
              },
              type: "PROMPT",
              ports: [
                {
                  id: "c678ddd0-f646-4bd3-9557-9ad63f6d8f3c",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              inputs: [
                {
                  id: "043a9f22-17c2-4d51-b106-753842a0c0b9",
                  key: "text",
                  value: {
                    rules: [
                      {
                        data: {
                          input_variable_id:
                            "991a53e2-9e1b-4d53-b214-f62bd7084f8b",
                        },
                        type: "INPUT_VARIABLE",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              trigger: {
                id: "0f3f518a-ce24-4355-8568-94e1bf295725",
                merge_behavior: "AWAIT_ANY",
              },
              adornments: [
                {
                  id: "65483f3d-59a3-4a8d-a8ab-70e6797cc474",
                  base: {
                    name: "RetryNode",
                    module: [
                      "vellum",
                      "workflows",
                      "nodes",
                      "core",
                      "retry_node",
                      "node",
                    ],
                  },
                  label: "Retry",
                  attributes: [
                    {
                      id: "25dec39b-be88-4ac5-a9ed-d9a9dd85774d",
                      name: "retry_on_error_code",
                      value: null,
                    },
                    {
                      id: "0e56a6b8-fb8d-4d38-8a24-4b3f34b34d8a",
                      name: "max_attempts",
                      value: {
                        type: "CONSTANT_VALUE",
                        value: { type: "NUMBER", value: 5.0 },
                      },
                    },
                  ],
                },
              ],
              definition: {
                name: "Prompt",
                module: ["testing", "nodes", "prompt"],
              },
              display_data: {
                width: 480.0,
                height: 175.0,
                comment: null,
                position: { x: 1971.8034185919948, y: 205.60253395092258 },
              },
            },
            {
              id: "e0dfea1e-391d-4dee-9d71-28b391106726",
              base: null,
              data: {
                name: "final-output",
                label: "Final Output",
                output_id: "162179ab-a85e-42d2-968e-79b5eb4ad683",
                output_type: "STRING",
                node_input_id: "cbc53e73-4246-4c28-805b-8a974fc8be48",
                target_handle_id: "fd2ee2c7-e9d8-42f4-9bc6-d22fe22a3044",
              },
              type: "TERMINAL",
              inputs: [
                {
                  id: "cbc53e73-4246-4c28-805b-8a974fc8be48",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        data: {
                          node_id: "82d5c288-aab8-4d27-bceb-4ba7bc688c34",
                          output_id: "e054f21d-33e1-4c76-8b1d-b22c393f6c7d",
                        },
                        type: "NODE_OUTPUT",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              trigger: {
                id: "fd2ee2c7-e9d8-42f4-9bc6-d22fe22a3044",
                merge_behavior: "AWAIT_ANY",
              },
              definition: {
                name: "FinalOutput",
                module: ["testing", "nodes", "final_output"],
              },
              display_data: {
                width: 449.0,
                height: 239.0,
                comment: null,
                position: { x: 2750.0, y: 210.0 },
              },
            },
          ],
          definition: { name: "Workflow", module: ["testing", "workflow"] },
          display_data: {
            viewport: {
              x: -1120.3947455205011,
              y: 146.5414971968781,
              zoom: 0.7661866549411893,
            },
          },
          output_values: [
            {
              value: {
                type: "NODE_OUTPUT",
                node_id: "e0dfea1e-391d-4dee-9d71-28b391106726",
                node_output_id: "162179ab-a85e-42d2-968e-79b5eb4ad683",
              },
              output_variable_id: "162179ab-a85e-42d2-968e-79b5eb4ad683",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "prompt.py"]);
      expectProjectFileToExist(["code", "display", "nodes", "prompt.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "prompt.py"]);
    });

    it("should generate try adornment node with correct attributes", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
          nodes: [
            {
              id: "inline-prompt-node",
              base: null,
              data: {
                label: "Prompt",
                variant: "INLINE",
                output_id: "959e7566-1e49-438d-9cd6-a2564b5e931b",
                exec_config: {
                  settings: null,
                  parameters: {},
                  input_variables: [],
                  prompt_template_block_data: {
                    blocks: [],
                    version: 1,
                  },
                },
                ml_model_name: "gpt-4o-mini",
                array_output_id: "7cffec7b-d1bc-432f-ac2a-f7ace819bf5f",
                error_output_id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                source_handle_id: "7556f35c-674d-45e3-9f88-74899bc03ea1",
                target_handle_id: "b22d4b55-41ac-4898-9374-8d2c4dd7e58e",
              },
              type: "PROMPT",
              ports: [],
              inputs: [],
              outputs: [],
              trigger: {},
              adornments: [
                {
                  id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                  base: {
                    name: "TryNode",
                    module: [
                      "vellum",
                      "workflows",
                      "nodes",
                      "core",
                      "try_node",
                      "node",
                    ],
                  },
                  label: "Try",
                  attributes: [
                    {
                      id: "b1bcf28e-a8d8-4746-9736-f96f7de73c73",
                      name: "on_error_code",
                      value: {
                        type: "CONSTANT_VALUE",
                        value: { type: "STRING", value: "INVALID_WORKFLOW" },
                      },
                    },
                  ],
                },
              ],
              attributes: [],
            },
            {
              id: "entrypoint-node",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "6a80add9-a37d-4280-bcc4-425c6e95b997",
              },
              type: "ENTRYPOINT",
              inputs: [],
            },
          ],
          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        runner_config: {},
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "generic_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      expectProjectFileToExist(["generic_test", "nodes", "prompt.py"]);
      expectProjectFileToExist([
        "generic_test",
        "display",
        "nodes",
        "prompt.py",
      ]);
      expectProjectFileToMatchSnapshot(["generic_test", "nodes", "prompt.py"]);
    });

    it("should correctly generate default code for adornments", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "dacda579-09e1-4244-8c2c-e024d24814af",
              type: "DEFAULT",
              source_node_id: "8f677851-0c8b-4ea2-9b44-71a48afe1b29",
              target_node_id: "46b280af-49aa-4bfc-b377-2ba80136f090",
              source_handle_id: "6a80add9-a37d-4280-bcc4-425c6e95b997",
              target_handle_id: "b22d4b55-41ac-4898-9374-8d2c4dd7e58e",
            },
            {
              id: "cd4ac61a-a326-44e2-bd60-737fcbfa9963",
              type: "DEFAULT",
              source_node_id: "46b280af-49aa-4bfc-b377-2ba80136f090",
              target_node_id: "a8c692de-383e-4184-9a83-9efb924cc45d",
              source_handle_id: "7556f35c-674d-45e3-9f88-74899bc03ea1",
              target_handle_id: "e251f19c-1ec7-453b-8d0f-419b7aae64fc",
            },
          ],
          nodes: [
            {
              id: "46b280af-49aa-4bfc-b377-2ba80136f090",
              base: null,
              data: {
                label: "Prompt",
                variant: "INLINE",
                output_id: "959e7566-1e49-438d-9cd6-a2564b5e931b",
                exec_config: {
                  settings: null,
                  parameters: {},
                  input_variables: [],
                  prompt_template_block_data: {
                    blocks: [],
                    version: 1,
                  },
                },
                ml_model_name: "gpt-4o-mini",
                array_output_id: "7cffec7b-d1bc-432f-ac2a-f7ace819bf5f",
                error_output_id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                source_handle_id: "7556f35c-674d-45e3-9f88-74899bc03ea1",
                target_handle_id: "b22d4b55-41ac-4898-9374-8d2c4dd7e58e",
              },
              type: "PROMPT",
              ports: [],
              inputs: [],
              outputs: [],
              trigger: {},
              adornments: [
                {
                  id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                  base: {
                    name: "TryNode",
                    module: [
                      "vellum",
                      "workflows",
                      "nodes",
                      "core",
                      "try_node",
                      "node",
                    ],
                  },
                  label: "Try",
                  attributes: [
                    {
                      id: "b1bcf28e-a8d8-4746-9736-f96f7de73c73",
                      name: "on_error_code",
                      value: null,
                    },
                  ],
                },
                {
                  id: "8792b525-e6cb-4c46-8c7e-1921b3597483",
                  base: {
                    name: "RetryNode",
                    module: [
                      "vellum",
                      "workflows",
                      "nodes",
                      "core",
                      "retry_node",
                      "node",
                    ],
                  },
                  label: "Retry",
                  attributes: [
                    {
                      id: "0e2fb942-c7b1-4123-8ee6-5b24514031b0",
                      name: "retry_on_error_code",
                      value: null,
                    },
                    {
                      id: "e242a0a9-bc6d-49fd-951d-3f01a4cc17fd",
                      name: "max_attempts",
                      value: {
                        type: "CONSTANT_VALUE",
                        value: { type: "NUMBER", value: 1.0 },
                      },
                    },
                    {
                      id: "38e8eb87-f99f-4cf9-846d-baab5612a65f",
                      name: "delay",
                      value: null,
                    },
                  ],
                },
              ],
              attributes: [],
            },
            {
              id: "8f677851-0c8b-4ea2-9b44-71a48afe1b29",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "6a80add9-a37d-4280-bcc4-425c6e95b997",
              },
              type: "ENTRYPOINT",
              inputs: [],
            },
          ],
          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "prompt.py"]);
      expectProjectFileToExist(["code", "display", "nodes", "prompt.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "prompt.py"]);
    });

    it("should correctly handle error code and custom string attribute types in adornments", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
          nodes: [
            {
              id: "inline-prompt-node",
              base: null,
              data: {
                label: "Prompt",
                variant: "INLINE",
                output_id: "959e7566-1e49-438d-9cd6-a2564b5e931b",
                exec_config: {
                  settings: null,
                  parameters: {},
                  input_variables: [],
                  prompt_template_block_data: {
                    blocks: [],
                    version: 1,
                  },
                },
                ml_model_name: "gpt-4o-mini",
                array_output_id: "7cffec7b-d1bc-432f-ac2a-f7ace819bf5f",
                error_output_id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                source_handle_id: "7556f35c-674d-45e3-9f88-74899bc03ea1",
                target_handle_id: "b22d4b55-41ac-4898-9374-8d2c4dd7e58e",
              },
              type: "PROMPT",
              ports: [],
              inputs: [],
              outputs: [],
              trigger: {},
              adornments: [
                {
                  id: "c204055c-fc9f-4fb5-9c58-babada7b0d89",
                  base: {
                    name: "TryNode",
                    module: [
                      "vellum",
                      "workflows",
                      "nodes",
                      "core",
                      "try_node",
                      "node",
                    ],
                  },
                  label: "Try",
                  attributes: [
                    {
                      id: "b1bcf28e-a8d8-4746-9736-f96f7de73c73",
                      name: "on_error_code",
                      value: {
                        type: "CONSTANT_VALUE",
                        value: { type: "STRING", value: "INVALID_WORKFLOW" },
                      },
                    },
                    {
                      id: "custom-attribute-id",
                      name: "custom_message",
                      value: {
                        type: "CONSTANT_VALUE",
                        value: {
                          type: "STRING",
                          value: "This is a regular string",
                        },
                      },
                    },
                  ],
                },
              ],
              attributes: [],
            },
            {
              id: "entrypoint-node",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "6a80add9-a37d-4280-bcc4-425c6e95b997",
              },
              type: "ENTRYPOINT",
              inputs: [],
            },
          ],
          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        runner_config: {},
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot(["code", "nodes", "prompt.py"]);
    });
  });
  describe("combinator normalization", () => {
    it("should normalize AND to OR combinators", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "edge-1",
              type: "DEFAULT",
              source_node_id: "entry",
              target_node_id: "terminal-node",
              source_handle_id: "entry_source",
              target_handle_id: "terminal_target",
            },
          ],
          nodes: [
            {
              id: "entry",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint",
                source_handle_id: "entry_source",
              },
              inputs: [],
            },
            {
              id: "terminal-node",
              type: "TERMINAL",
              data: {
                label: "Final Output",
                name: "final-output",
                target_handle_id: "terminal_target",
                output_id: "terminal_output_id",
                output_type: "STRING",
                node_input_id: "terminal_input",
              },
              inputs: [
                {
                  id: "terminal_input",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        data: { type: "NUMBER", value: 3.0 },
                        type: "CONSTANT_VALUE",
                      },
                    ],
                    combinator: "AND", // This should be normalized to OR
                  },
                },
              ],
              outputs: [
                {
                  id: "some-id",
                  name: "node_input",
                  type: "NUMBER",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 3.0,
                    },
                  },
                },
              ],
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "final_output.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "final_output.py"]);
    });
  });
  describe("should escape special characters", () => {
    it("should handle node comments with quotes at the beginning and end", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "test-edge-1",
              type: "DEFAULT",
              source_node_id: "entry-node",
              target_node_id: "templating-node",
              source_handle_id: "entry_source",
              target_handle_id: "template_target",
            },
          ],
          nodes: [
            {
              id: "entry-node",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint",
                source_handle_id: "entry_source",
              },
              inputs: [],
              display_data: {
                width: 124,
                height: 48,
                comment: null,
                position: { x: 100, y: 100 },
              },
            },
            {
              id: "templating-node",
              type: "TEMPLATING",
              data: {
                label: "Templating Node",
                template_node_input_id: "template_input",
                output_id: "output",
                output_type: "STRING",
                source_handle_id: "template_source",
                target_handle_id: "template_target",
              },
              inputs: [
                {
                  id: "template_input",
                  key: "template",
                  value: {
                    combinator: "OR",
                    rules: [
                      {
                        type: "CONSTANT_VALUE",
                        data: {
                          type: "STRING",
                          value: "test template",
                        },
                      },
                    ],
                  },
                },
              ],
              display_data: {
                width: 300,
                height: 200,
                comment: {
                  value: '"Hello" "World"',
                  expanded: false,
                },
                position: { x: 300, y: 100 },
              },
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "templating_node.py"]);
    });

    it("should not escape single quotes in node comments", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "test-edge-1",
              type: "DEFAULT",
              source_node_id: "entry-node",
              target_node_id: "templating-node",
              source_handle_id: "entry_source",
              target_handle_id: "template_target",
            },
          ],
          nodes: [
            {
              id: "entry-node",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint",
                source_handle_id: "entry_source",
              },
              inputs: [],
              display_data: {
                width: 124,
                height: 48,
                comment: null,
                position: { x: 100, y: 100 },
              },
            },
            {
              id: "templating-node",
              type: "TEMPLATING",
              data: {
                label: "Templating Node",
                template_node_input_id: "template_input",
                output_id: "output",
                output_type: "STRING",
                source_handle_id: "template_source",
                target_handle_id: "template_target",
              },
              inputs: [
                {
                  id: "template_input",
                  key: "template",
                  value: {
                    combinator: "OR",
                    rules: [
                      {
                        type: "CONSTANT_VALUE",
                        data: {
                          type: "STRING",
                          value: "test template",
                        },
                      },
                    ],
                  },
                },
              ],
              display_data: {
                width: 300,
                height: 200,
                comment: {
                  value: "'Hello' 'World'",
                  expanded: false,
                },
                position: { x: 300, y: 100 },
              },
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "templating_node.py"]);
    });
  });
  describe("Get generic node files", () => {
    it("should get generic node files", async () => {
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
              id: "generic-node",
              type: "GENERIC",
              label: "Generic Node",
              attributes: [],
              trigger: {
                id: "generic-node-trigger",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: "generic-node-default-port",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              outputs: [],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "generic-node",
              target_handle_id: "generic-node-trigger",
              type: "DEFAULT",
              id: "edge_1",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        runner_config: {},
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "generic_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      const pythonCodeMergeableNodeFiles =
        project.getPythonCodeMergeableNodeFiles();
      expect(pythonCodeMergeableNodeFiles).toEqual(
        new Set(["nodes/generic_node.py"])
      );
    });

    it("should not get generic node files", async () => {
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
              id: "some-node-id",
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
              ],
            },
          ],
          edges: [
            {
              id: "edge_1",
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "some-node-id",
              target_handle_id: "template_target",
              type: "DEFAULT",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        runner_config: {},
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "generic_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      const pythonCodeMergeableNodeFiles =
        project.getPythonCodeMergeableNodeFiles();
      expect(pythonCodeMergeableNodeFiles).toEqual(new Set());
    });
    it("should exclude core, displayable, and experimental nodes from mergeable node files", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
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
              id: "core-node",
              base: {
                name: "CoreNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "core_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "CoreNode",
              ports: [
                {
                  id: "7b97f998-4be5-478d-94c4-9423db5f6392",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "73a3c1e6-b632-45c5-a837-50922ccf0d47",
                  name: "text",
                  type: "STRING",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "" },
                  },
                },
                {
                  id: "7dfce73d-3d56-4bb6-8a7e-cc1b3e38746e",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: [] },
                  },
                },
              ],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [],
            },
            {
              id: "displayable-node",
              base: {
                name: "DisplayableNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "displayable_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "DisplayableNode",
              ports: [
                {
                  id: "7b97f998-4be5-478d-94c4-9423db5f6392",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "73a3c1e6-b632-45c5-a837-50922ccf0d47",
                  name: "text",
                  type: "STRING",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "" },
                  },
                },
                {
                  id: "7dfce73d-3d56-4bb6-8a7e-cc1b3e38746e",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: [] },
                  },
                },
              ],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [],
            },
            {
              id: "tool-calling-node",
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "experimental",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "ToolCallingNode",
              ports: [
                {
                  id: "7b97f998-4be5-478d-94c4-9423db5f6392",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "73a3c1e6-b632-45c5-a837-50922ccf0d47",
                  name: "text",
                  type: "STRING",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "" },
                  },
                },
                {
                  id: "7dfce73d-3d56-4bb6-8a7e-cc1b3e38746e",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: [] },
                  },
                },
              ],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [],
            },
          ],
        },
        input_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "generic_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      const pythonCodeMergeableNodeFiles =
        project.getPythonCodeMergeableNodeFiles();
      expect(pythonCodeMergeableNodeFiles).toEqual(new Set());
    });
  });
  describe("LazyReference", () => {
    it("should not generate LazyReference when there is a long branch", async () => {
      //   graph = (
      //     {
      //         parallel-node-1
      //         >> seq-node-1
      //         >> seq-node-2
      //         >> request-body-node,
      //         parallel-node-2
      //     }
      //     >> MergeNode
      //     >> APINode
      //     >> FinalOutput
      // )
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "edge-1",
              type: "DEFAULT",
              source_node_id: "entrypoint-node",
              target_node_id: "parallel-node-1",
              source_handle_id: "2667ea0e-9ef6-4731-8478-43f2d2afa4de",
              target_handle_id: "15913e7a-5f25-40b8-84a3-f15fe490da55",
            },
            {
              id: "edge-2",
              type: "DEFAULT",
              source_node_id: "seq-node-1",
              target_node_id: "seq-node-2",
              source_handle_id: "436591c9-ae12-405f-9b56-81c71f4d6065",
              target_handle_id: "34d16931-3161-4c47-b9ad-9055a05ee511",
            },
            {
              id: "edge-3",
              type: "DEFAULT",
              source_node_id: "parallel-node-1",
              target_node_id: "seq-node-1",
              source_handle_id: "0baeef65-7205-4db3-a111-dfb11b5e0184",
              target_handle_id: "0ab49640-f504-4f7c-99be-66a8c0597ccf",
            },
            {
              id: "edge-4",
              type: "DEFAULT",
              source_node_id: "seq-node-2",
              target_node_id: "request-body-node",
              source_handle_id: "7a1bca72-7c7e-4523-ad65-8bd19d4b12ed",
              target_handle_id: "e55a5921-0cd9-4c8e-b8ec-cbd42f91e935",
            },
            {
              id: "edge-5",
              type: "DEFAULT",
              source_node_id: "request-body-node",
              target_node_id: "merge-node",
              source_handle_id: "2bb42ef4-3ef7-4b07-8790-ca74c1a3ac4d",
              target_handle_id: "b8e75fdf-30d2-4051-9531-ee1b2116ecb1",
            },
            {
              id: "edge-6",
              type: "DEFAULT",
              source_node_id: "parallel-node-2",
              target_node_id: "merge-node",
              source_handle_id: "dab065ab-349a-4a6b-b34d-7d10e1475349",
              target_handle_id: "429e7230-cbfc-47b9-b43e-bd22c50d565c",
            },
            {
              id: "edge-7",
              type: "DEFAULT",
              source_node_id: "merge-node",
              target_node_id: "api-node",
              source_handle_id: "f65dc3ac-cad7-4b24-a0f9-112f6e13a7b7",
              target_handle_id: "d480a94a-678b-41c6-86d2-5178b49ca1b4",
            },
            {
              id: "edge-8",
              type: "DEFAULT",
              source_node_id: "api-node",
              target_node_id: "final-output-node",
              source_handle_id: "468fcd8c-1bc5-4519-99a5-f2a29b19fa1a",
              target_handle_id: "8cc17648-7940-4821-b603-99f5e61366dc",
            },
            {
              id: "54fb5a58-ebf2-4347-92d6-947bfe21fe58",
              type: "DEFAULT",
              source_node_id: "entrypoint-node",
              target_node_id: "parallel-node-2",
              source_handle_id: "2667ea0e-9ef6-4731-8478-43f2d2afa4de",
              target_handle_id: "85ad292c-569f-4451-9747-9e8b7300c518",
            },
          ],
          nodes: [
            {
              id: "merge-node",
              base: null,
              data: {
                label: "Merge Node",
                merge_strategy: "AWAIT_ALL",
                target_handles: [
                  { id: "b8e75fdf-30d2-4051-9531-ee1b2116ecb1" },
                  { id: "429e7230-cbfc-47b9-b43e-bd22c50d565c" },
                ],
                source_handle_id: "f65dc3ac-cad7-4b24-a0f9-112f6e13a7b7",
              },
              type: "MERGE",
              ports: [],
              inputs: [],
              definition: null,
            },
            {
              id: "parallel-node-2",
              base: null,
              data: {
                label: "Parallel Node 2",
                output_id: "1f084b44-bbab-4495-bed0-11e13313c676",
                output_type: "STRING",
                error_output_id: null,
                source_handle_id: "dab065ab-349a-4a6b-b34d-7d10e1475349",
                target_handle_id: "85ad292c-569f-4451-9747-9e8b7300c518",
                template_node_input_id: "63795ac6-e197-4ada-998b-ac18ca875696",
              },
              type: "TEMPLATING",
              ports: [],
              inputs: [],
              outputs: null,
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "api-node",
              base: null,
              data: {
                label: "API Node",
                url_input_id: "866d0466-9eb9-4a14-963c-db9d2253c2ab",
                body_input_id: "38219078-d3cc-4059-906a-6091428baeb8",
                json_output_id: "de6c95b6-b325-42b4-8232-46221604013f",
                text_output_id: "20b7f27a-7144-45a1-9ab8-e34889826f8d",
                error_output_id: null,
                method_input_id: "d0547072-c7cd-45f2-9668-6afeba5c1735",
                source_handle_id: "468fcd8c-1bc5-4519-99a5-f2a29b19fa1a",
                target_handle_id: "d480a94a-678b-41c6-86d2-5178b49ca1b4",
                additional_headers: [],
                status_code_output_id: "a7e4bceb-f187-489b-b554-72ce8c92bcbf",
                api_key_header_key_input_id:
                  "d65868b0-4d4d-4573-a66a-fca8b82496bb",
                authorization_type_input_id:
                  "592656b1-b527-4d32-821d-488f0ce1bfbe",
                bearer_token_value_input_id:
                  "13894fb1-b8b0-41a2-ba52-cde0ffd41386",
                api_key_header_value_input_id:
                  "9de2d5a2-89ad-4d1b-bdb7-04dc1b9c115a",
              },
              type: "API",
              ports: [],
              inputs: [
                {
                  id: "d0547072-c7cd-45f2-9668-6afeba5c1735",
                  key: "method",
                  value: {
                    rules: [
                      {
                        data: { type: "STRING", value: "POST" },
                        type: "CONSTANT_VALUE",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "866d0466-9eb9-4a14-963c-db9d2253c2ab",
                  key: "url",
                  value: {
                    rules: [
                      {
                        data: {
                          node_id: "parallel-node-2",
                          output_id: "1f084b44-bbab-4495-bed0-11e13313c676",
                        },
                        type: "NODE_OUTPUT",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "38219078-d3cc-4059-906a-6091428baeb8",
                  key: "body",
                  value: {
                    rules: [
                      {
                        data: {
                          node_id: "request-body-node",
                          output_id: "393b0c22-47b2-48de-b018-82fbe67ee965",
                        },
                        type: "NODE_OUTPUT",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "592656b1-b527-4d32-821d-488f0ce1bfbe",
                  key: "authorization_type",
                  value: {
                    rules: [
                      {
                        data: { type: "STRING", value: "BEARER_TOKEN" },
                        type: "CONSTANT_VALUE",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "13894fb1-b8b0-41a2-ba52-cde0ffd41386",
                  key: "bearer_token_value",
                  value: {
                    rules: [
                      {
                        data: {
                          type: "STRING",
                          workspace_secret_id:
                            "f295ac8f-2e82-481c-ba19-98ba97252696",
                        },
                        type: "WORKSPACE_SECRET",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "d65868b0-4d4d-4573-a66a-fca8b82496bb",
                  key: "api_key_header_key",
                  value: {
                    rules: [
                      {
                        data: { type: "STRING", value: null },
                        type: "CONSTANT_VALUE",
                      },
                    ],
                    combinator: "OR",
                  },
                },
                {
                  id: "9de2d5a2-89ad-4d1b-bdb7-04dc1b9c115a",
                  key: "api_key_header_value",
                  value: {
                    rules: [
                      {
                        data: { type: "STRING", workspace_secret_id: null },
                        type: "WORKSPACE_SECRET",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              outputs: null,
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "request-body-node",
              base: null,
              data: {
                label: "Request Body Node",
                output_id: "393b0c22-47b2-48de-b018-82fbe67ee965",
                output_type: "JSON",
                error_output_id: null,
                source_handle_id: "2bb42ef4-3ef7-4b07-8790-ca74c1a3ac4d",
                target_handle_id: "749a2f14-cec0-4d34-a4fa-fb8fd269fed8",
                template_node_input_id: "f19b1132-ca0c-4b1d-afe5-bd0833fe6b89",
              },
              type: "TEMPLATING",
              ports: [],
              inputs: [],
              outputs: null,
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "parallel-node-1",
              base: null,
              data: {
                label: "Parallel Node 1",
                output_id: "fe4be5d9-4c5a-4e8d-857a-d73a809ce17d",
                output_type: "STRING",
                error_output_id: null,
                source_handle_id: "0baeef65-7205-4db3-a111-dfb11b5e0184",
                target_handle_id: "15913e7a-5f25-40b8-84a3-f15fe490da55",
                template_node_input_id: "10a8f721-9980-4b9a-9384-254ec1866b02",
              },
              type: "TEMPLATING",
              ports: [],
              inputs: [],
              outputs: null,
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "seq-node-2",
              base: null,
              data: {
                label: "Seq Node 2",
                variant: "DEPLOYMENT",
                output_id: "5c3864a5-0aa6-402d-8f84-5c113219f408",
                release_tag: "LATEST",
                array_output_id: "f2741add-1d83-449c-ade8-7ffb9aa3c1fa",
                error_output_id: null,
                source_handle_id: "7a1bca72-7c7e-4523-ad65-8bd19d4b12ed",
                target_handle_id: "34d16931-3161-4c47-b9ad-9055a05ee511",
                ml_model_fallbacks: [],
                prompt_deployment_id: "ef1eea88-8dfa-431e-8bde-163ea5e635e2",
              },
              type: "PROMPT",
              ports: [],
              inputs: [],
              outputs: [],
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "seq-node-1",
              base: null,
              data: {
                label: "Seq Node 1",
                url_input_id: "c8cdf994-ada3-4813-9e79-b11c84e2eaaf",
                body_input_id: "5752bb47-1346-405e-aa1a-2fdbda8e7b79",
                json_output_id: "8e32e235-0a8e-4596-987e-927eb66aa6f6",
                text_output_id: "624b484e-8991-4c4f-9403-75b477d7dc46",
                error_output_id: null,
                method_input_id: "e6b4c461-ff82-40d2-8e53-2646198a8d36",
                source_handle_id: "436591c9-ae12-405f-9b56-81c71f4d6065",
                target_handle_id: "0ab49640-f504-4f7c-99be-66a8c0597ccf",
                additional_headers: [],
                status_code_output_id: "4cce55f8-fa0e-44b8-811b-35e9252d149c",
                api_key_header_key_input_id:
                  "3ebf4273-dded-4e9e-a9b6-15096e60c2e5",
                authorization_type_input_id:
                  "f1aae5a3-9a6c-4995-aa74-bae54b74a544",
                bearer_token_value_input_id:
                  "00672750-b19c-4661-86b0-8d250805be1a",
                api_key_header_value_input_id:
                  "bac82cd0-4a34-42ef-a08f-c2567dc71ac8",
              },
              type: "API",
              ports: [],
              inputs: [],
              outputs: null,
              trigger: {},
              adornments: null,
              definition: null,
            },
            {
              id: "entrypoint-node",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "2667ea0e-9ef6-4731-8478-43f2d2afa4de",
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
            },
            {
              id: "final-output-node",
              base: null,
              data: {
                name: "final-output",
                label: "Final Output",
                output_id: "baeb6244-b88b-4bf8-a6a3-7212d9922ae4",
                output_type: "STRING",
                node_input_id: "63a6d2c9-fffa-40cb-96ab-017cdd040b9f",
                target_handle_id: "8cc17648-7940-4821-b603-99f5e61366dc",
              },
              type: "TERMINAL",
              inputs: [],
              trigger: {},
              definition: null,
            },
          ],
          definition: null,
          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot(["code", "nodes", "api_node.py"]);
    });

    it("should not generate LazyReference when there is a simple loop", async () => {
      //   graph = (
      //     StartNode >> {
      //         RouterNode.Ports.top >> TopNode >> StartNode,
      //         RouterNode.Ports.bottom >> BottomNode,
      //     }
      // )
      const entrypointNodeId = uuidv4();
      const entrypointSourceHandleId = uuidv4();

      const startNodeId = uuidv4();
      const startSourceHandleId = uuidv4();
      const startTargetHandleId = uuidv4();
      const startOutputId = uuidv4();

      const routerNodeId = uuidv4();
      const routerIfSourceHandleId = uuidv4();
      const routerElseSourceHandleId = uuidv4();
      const routerTargetHandleId = uuidv4();

      const topNodeId = uuidv4();
      const topSourceHandleId = uuidv4();
      const topTargetHandleId = uuidv4();

      const bottomNodeId = uuidv4();
      const bottomTargetHandleId = uuidv4();

      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "edge-1",
              type: "DEFAULT",
              source_node_id: entrypointNodeId,
              target_node_id: startNodeId,
              source_handle_id: entrypointSourceHandleId,
              target_handle_id: startTargetHandleId,
            },
            {
              id: "edge-2",
              type: "DEFAULT",
              source_node_id: startNodeId,
              target_node_id: routerNodeId,
              source_handle_id: startSourceHandleId,
              target_handle_id: routerTargetHandleId,
            },
            {
              id: "edge-3",
              type: "DEFAULT",
              source_node_id: routerNodeId,
              target_node_id: topNodeId,
              source_handle_id: routerIfSourceHandleId,
              target_handle_id: topTargetHandleId,
            },
            {
              id: "edge-4",
              type: "DEFAULT",
              source_node_id: topNodeId,
              target_node_id: bottomNodeId,
              source_handle_id: routerElseSourceHandleId,
              target_handle_id: bottomTargetHandleId,
            },
            {
              id: "edge-5",
              type: "DEFAULT",
              source_node_id: topNodeId,
              target_node_id: startNodeId,
              source_handle_id: topSourceHandleId,
              target_handle_id: startTargetHandleId,
            },
          ],
          nodes: [
            {
              id: entrypointNodeId,
              data: {
                label: "Entrypoint Node",
                source_handle_id: entrypointSourceHandleId,
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
            },
            {
              id: startNodeId,
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              type: "GENERIC",
              label: "Start Node",
              trigger: {
                id: startTargetHandleId,
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: startSourceHandleId,
                  type: "DEFAULT",
                  name: "default",
                },
              ],
              outputs: [
                {
                  id: startOutputId,
                  type: "STRING",
                  name: "result",
                  value: null,
                },
              ],
              attributes: [],
              definition: null,
            },
            {
              id: routerNodeId,
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              type: "GENERIC",
              label: "Router Node",
              trigger: {
                id: routerTargetHandleId,
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: routerIfSourceHandleId,
                  type: "IF",
                  name: "top",
                  expression: {
                    type: "BINARY_EXPRESSION",
                    operator: "=",
                    lhs: {
                      type: "NODE_OUTPUT",
                      node_id: startNodeId,
                      node_output_id: startOutputId,
                    },
                    rhs: {
                      type: "CONSTANT_VALUE",
                      value: {
                        type: "STRING",
                        value: "top",
                      },
                    },
                  },
                },
                {
                  id: routerElseSourceHandleId,
                  type: "ELSE",
                  name: "bottom",
                },
              ],
              outputs: [],
              attributes: [],
              definition: null,
            },
            {
              id: topNodeId,
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              type: "GENERIC",
              label: "Top Node",
              trigger: {
                id: topTargetHandleId,
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: topSourceHandleId,
                  type: "DEFAULT",
                  name: "default",
                },
              ],
              outputs: [],
              attributes: [],
              definition: null,
            },
            {
              id: bottomNodeId,
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              type: "GENERIC",
              label: "Bottom Node",
              trigger: {
                id: bottomTargetHandleId,
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [],
              outputs: [],
              attributes: [],
              definition: null,
            },
          ],
          definition: null,
          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot(["code", "nodes", "router_node.py"]);
    });
  });

  describe("modules", () => {
    it("should generate code in the same module as the project", async () => {
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
              id: "templating",
              type: "TEMPLATING",
              data: {
                label: "Templating Node",
                template_node_input_id: "template",
                output_id: "output",
                output_type: "STRING",
                source_handle_id: "template_source",
                target_handle_id: "template_target",
              },
              definition: {
                name: "TemplatingNode",
                module: ["my", "module", "templating_node"],
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
              ],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "templating",
              target_handle_id: "template_target",
              type: "DEFAULT",
              id: "edge_1",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "my.module",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToExist(["my", "module", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot([
        "my",
        "module",
        "nodes",
        "templating_node.py",
      ]);
    });
  });

  describe("state", () => {
    it("should generate a state.py file", async () => {
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
              id: "templating",
              type: "TEMPLATING",
              data: {
                label: "Templating Node",
                template_node_input_id: "template",
                output_id: "output",
                output_type: "STRING",
                source_handle_id: "template_source",
                target_handle_id: "template_target",
              },
              definition: {
                name: "TemplatingNode",
                module: ["my", "module", "templating_node"],
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
              ],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "templating",
              target_handle_id: "template_target",
              type: "DEFAULT",
              id: "edge_1",
            },
          ],
        },
        input_variables: [],
        output_variables: [],
        state_variables: [
          {
            // hardcoded id for display file snapshot
            id: "5bc5356a-154f-4bba-a8ee-eb283bfd2a25",
            key: "foo",
            type: "STRING",
          },
        ],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot(["code", "state.py"]);
      expectProjectFileToMatchSnapshot(["code", "display", "workflow.py"]);
      expectProjectFileToMatchSnapshot(["code", "workflow.py"]);
    });
  });
  describe("function", () => {
    it("should generate <function_name>.py file", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
          nodes: [
            {
              id: "entrypoint",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "d8144c82-8b1a-4181-b068-6aaf69d21b73",
              },
              type: "ENTRYPOINT",
              inputs: [],
            },
            {
              id: "tool-calling-node",
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "experimental",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "GetCurrentWeatherNode",
              ports: [
                {
                  id: "7b97f998-4be5-478d-94c4-9423db5f6392",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "73a3c1e6-b632-45c5-a837-50922ccf0d47",
                  name: "text",
                  type: "STRING",
                  value: null,
                },
                {
                  id: "7dfce73d-3d56-4bb6-8a7e-cc1b3e38746e",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: null,
                },
              ],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [
                {
                  id: "75bd1347-dca2-4cba-b0b0-a20a2923ebcc",
                  name: "ml_model",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "gpt-4o-mini" },
                  },
                },
                {
                  id: "723f614a-be30-4f27-90d0-896c740e58d3",
                  name: "max_tool_calls",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "NUMBER", value: 3.0 },
                  },
                },
                {
                  id: "beec5344-2eff-47d2-b920-b90367370d79",
                  name: "blocks",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          state: null,
                          blocks: [
                            {
                              state: null,
                              blocks: [
                                {
                                  text: "You are a weather expert",
                                  state: null,
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
                                },
                              ],
                              block_type: "RICH_TEXT",
                              cache_config: null,
                            },
                          ],
                          chat_role: "SYSTEM",
                          block_type: "CHAT_MESSAGE",
                          chat_source: null,
                          cache_config: null,
                          chat_message_unterminated: null,
                        },
                        {
                          state: null,
                          blocks: [
                            {
                              state: null,
                              blocks: [
                                {
                                  state: null,
                                  block_type: "VARIABLE",
                                  cache_config: null,
                                  input_variable: "question",
                                },
                              ],
                              block_type: "RICH_TEXT",
                              cache_config: null,
                            },
                          ],
                          chat_role: "USER",
                          block_type: "CHAT_MESSAGE",
                          chat_source: null,
                          cache_config: null,
                          chat_message_unterminated: null,
                        },
                      ],
                    },
                  },
                },
                {
                  id: "7b1ab802-3228-43b3-a493-734c94794710",
                  name: "functions",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          src: 'def get_current_weather(location: str, unit: str) -> str:\n    """\n    Get the current weather in a given location.\n    """\n    return f"The current weather in {location} is sunny with a temperature of 70 degrees {unit}."\n',
                          definition: {
                            name: "get_current_weather",
                            state: null,
                            forced: null,
                            strict: null,
                            parameters: {
                              type: "object",
                              required: ["location", "unit"],
                              properties: {
                                unit: { type: "string" },
                                location: { type: "string" },
                              },
                            },
                            description: null,
                            cache_config: null,
                          },
                        },
                        {
                          src: `def format_answer(answer: str) -> str:\n    """\n    Format the answer and request the LLM to provide a final text summary.\n    """\n    formatted = f"The answer to the question is: {answer}"\n    return (\n        f"{formatted}\\n\\nNow please provide a final summary with any temperature conversions or additional information."\n    )\n`,
                          definition: {
                            name: "format_answer",
                            state: null,
                            forced: null,
                            strict: null,
                            parameters: {
                              type: "object",
                              required: ["answer"],
                              properties: { answer: { type: "string" } },
                            },
                            description: null,
                            cache_config: null,
                          },
                        },
                      ],
                    },
                  },
                },
                {
                  id: "38cf126e-a186-4a63-8e30-47c4507413cd",
                  name: "prompt_inputs",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: {
                        question: "What's the weather like in San Francisco?",
                      },
                    },
                  },
                },
              ],
              definition: {
                name: "GetCurrentWeatherNode",
                module: ["testing", "nodes", "tool_call"],
              },
            },
          ],

          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "get_current_weather_node_functions",
        "__init__.py",
      ]);
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "get_current_weather_node_functions",
        "get_current_weather.py",
      ]);
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "get_current_weather_node_functions",
        "format_answer.py",
      ]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "tool_call.py"]);
    });
    it("should generate empty function array if no functions are defined", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
          nodes: [
            {
              id: "entrypoint",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "d8144c82-8b1a-4181-b068-6aaf69d21b73",
              },
              type: "ENTRYPOINT",
              inputs: [],
            },
            {
              id: "tool-calling-node",
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "experimental",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "GetCurrentWeatherNode",
              ports: [
                {
                  id: "7b97f998-4be5-478d-94c4-9423db5f6392",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "73a3c1e6-b632-45c5-a837-50922ccf0d47",
                  name: "text",
                  type: "STRING",
                  value: null,
                },
                {
                  id: "7dfce73d-3d56-4bb6-8a7e-cc1b3e38746e",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: null,
                },
              ],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [
                {
                  id: "75bd1347-dca2-4cba-b0b0-a20a2923ebcc",
                  name: "ml_model",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "gpt-4o-mini" },
                  },
                },
                {
                  id: "723f614a-be30-4f27-90d0-896c740e58d3",
                  name: "max_tool_calls",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "NUMBER", value: 3.0 },
                  },
                },
                {
                  id: "beec5344-2eff-47d2-b920-b90367370d79",
                  name: "blocks",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          state: null,
                          blocks: [
                            {
                              state: null,
                              blocks: [
                                {
                                  text: "You are a weather expert",
                                  state: null,
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
                                },
                              ],
                              block_type: "RICH_TEXT",
                              cache_config: null,
                            },
                          ],
                          chat_role: "SYSTEM",
                          block_type: "CHAT_MESSAGE",
                          chat_source: null,
                          cache_config: null,
                          chat_message_unterminated: null,
                        },
                        {
                          state: null,
                          blocks: [
                            {
                              state: null,
                              blocks: [
                                {
                                  state: null,
                                  block_type: "VARIABLE",
                                  cache_config: null,
                                  input_variable: "question",
                                },
                              ],
                              block_type: "RICH_TEXT",
                              cache_config: null,
                            },
                          ],
                          chat_role: "USER",
                          block_type: "CHAT_MESSAGE",
                          chat_source: null,
                          cache_config: null,
                          chat_message_unterminated: null,
                        },
                      ],
                    },
                  },
                },
                {
                  id: "7b1ab802-3228-43b3-a493-734c94794710",
                  name: "functions",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [],
                    },
                  },
                },
                {
                  id: "38cf126e-a186-4a63-8e30-47c4507413cd",
                  name: "prompt_inputs",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: {
                        question: "What's the weather like in San Francisco?",
                      },
                    },
                  },
                },
              ],
              definition: {
                name: "GetCurrentWeatherNode",
                module: ["testing", "nodes", "tool_call"],
              },
            },
          ],

          output_values: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        options: {
          disableFormatting: true,
        },
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot(["code", "nodes", "tool_call.py"]);
    });
  });
});
