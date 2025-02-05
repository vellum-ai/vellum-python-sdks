import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { difference } from "lodash";
import { v4 as uuidv4 } from "uuid";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
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
          "simple_workflow_node_with_output_values",
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
      });

      await project.generateCode();

      const workflowPath = join(
        tempDir,
        project.getModuleName(),
        "workflow.py"
      );
      expect(fs.existsSync(workflowPath)).toBe(true);
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
      });

      await project.generateCode();

      const nodesPath = join(tempDir, project.getModuleName(), "nodes");
      const nodeFiles = fs.readdirSync(nodesPath);
      expect(nodeFiles).toContain("templating_node.py");
      expect(nodeFiles).toContain("templating_node_1.py");
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
        strict: true,
      });

      await project.generateCode();

      const scriptPath = join(
        tempDir,
        project.getModuleName(),
        "nodes",
        "code_execution_node",
        "script.py"
      );
      expect(fs.existsSync(scriptPath)).toBe(true);
      expect(fs.readFileSync(scriptPath, "utf-8")).toMatchSnapshot();
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
    it.skip("should generate a proper Lazy Reference for the first node", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
        strict: false,
      });

      await project.generateCode();

      const errorLogPath = join(tempDir, project.getModuleName(), "error.log");
      const errorLog = fs.existsSync(errorLogPath)
        ? fs.readFileSync(errorLogPath, "utf-8")
        : "";
      expect(errorLog).toBe("");

      const scriptPath = join(
        tempDir,
        project.getModuleName(),
        "nodes",
        "first_node.py"
      );
      expect(fs.existsSync(scriptPath)).toBe(true);
      expect(fs.readFileSync(scriptPath, "utf-8")).toMatchSnapshot();
    });
  });
});
