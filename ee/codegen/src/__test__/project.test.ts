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

  function expectProjectFileToMatchSnapshot(
    project: WorkflowProjectGenerator,
    filePath: string[]
  ) {
    const completeFilePath = join(
      tempDir,
      project.getModuleName(),
      ...filePath
    );
    expect(fs.existsSync(completeFilePath)).toBe(true);
    expect(fs.readFileSync(completeFilePath, "utf-8")).toMatchSnapshot();
  }

  function expectProjectFileToExist(
    project: WorkflowProjectGenerator,
    filePath: string[]
  ) {
    const completeFilePath = join(
      tempDir,
      project.getModuleName(),
      ...filePath
    );
    expect(fs.existsSync(completeFilePath)).toBe(true);
  }

  function expectErrorLog(
    project: WorkflowProjectGenerator,
    expectedContents: string = ""
  ) {
    const errorLogPath = join(tempDir, project.getModuleName(), "error.log");
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
    };
    vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockImplementation(
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

      expectProjectFileToExist(project, ["workflow.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "bad_node.py"]);

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

      expectProjectFileToExist(project, ["workflow.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "bad_node.py"]);
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

      expectProjectFileToMatchSnapshot(project, ["sandbox.py"]);
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

      expectProjectFileToMatchSnapshot(project, ["workflow.py"]);
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

      expectProjectFileToExist(project, ["nodes", "templating_node.py"]);
      expectProjectFileToExist(project, ["nodes", "templating_node_1.py"]);
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

      expectProjectFileToMatchSnapshot(project, [
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

      expectErrorLog(project);
      expectProjectFileToMatchSnapshot(project, ["nodes", "first_node.py"]);
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

      expectProjectFileToExist(project, ["nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "final_output.py"]);
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
      expectErrorLog(project);

      // We should have generated a Workflow that has a graph containing only the first node
      expectProjectFileToMatchSnapshot(project, ["workflow.py"]);

      // We should have generated a file for the second node, even though it's not in the graph
      expectProjectFileToMatchSnapshot(project, ["nodes", "second_node.py"]);

      // We should have generated a display file for the second node
      expectProjectFileToMatchSnapshot(project, [
        "display",
        "nodes",
        "second_node.py",
      ]);

      // We should have included the second node in our init files
      expectProjectFileToMatchSnapshot(project, ["nodes", "__init__.py"]);
      expectProjectFileToMatchSnapshot(project, [
        "display",
        "nodes",
        "__init__.py",
      ]);
    });
    it("should not generate unused_graphs if final output is not used", async () => {
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
              attributes: [
                {
                  id: uuidv4(),
                  name: "forward",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "generic-node",
                    node_output_id: "output",
                  },
                },
              ],
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
      expectProjectFileToMatchSnapshot(project, ["workflow.py"]);
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

      expectProjectFileToExist(project, ["nodes", "final_output.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "final_output.py"]);
    });
  });
  describe("retry node adornment", () => {
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

      expectProjectFileToExist(project, ["nodes", "prompt.py"]);
      expectProjectFileToExist(project, ["display", "nodes", "prompt.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "prompt.py"]);
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
            },
          ],
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

      expectProjectFileToExist(project, ["nodes", "final_output.py"]);
      expectProjectFileToMatchSnapshot(project, ["nodes", "final_output.py"]);
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
      expectProjectFileToExist(project, ["nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(project, [
        "nodes",
        "templating_node.py",
      ]);
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
      expectProjectFileToExist(project, ["nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(project, [
        "nodes",
        "templating_node.py",
      ]);
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
              attributes: [
                {
                  id: uuidv4(),
                  name: "forward",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "generic-node",
                    node_output_id: "output",
                  },
                },
              ],
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
  });
});
