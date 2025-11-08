import { mkdir, readdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { difference } from "lodash";
import { v4 as uuidv4 } from "uuid";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { MlModels } from "vellum-ai/api/resources/mlModels/client/Client";
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
import {
  NodeAttribute as NodeAttributeType,
  WorkflowNodeType,
} from "src/types/vellum";

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
    const snapshotName = filePath.join("/");
    expect(fs.readFileSync(completeFilePath, "utf-8")).toMatchSnapshot(
      snapshotName
    );
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

  it("getNodeIdToFileMapping returns definitions for nodes with definition", async () => {
    const displayData = {
      workflow_raw_data: {
        nodes: [
          {
            id: "9663d2e9-8e18-448b-b963-cac4539db9d7",
            type: "ENTRYPOINT",
            data: {
              label: "Entrypoint",
              source_handle_id: "entry_source",
              target_handle_id: "entry_target",
            },
            inputs: [],
          },
          {
            id: "4344baa3-cdfe-4c16-bb76-545e0f55dba9",
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
            definition: {
              name: "Generic Node",
              module: ["my_nodes", "my_custom_node"],
            },
            outputs: [],
          },
          {
            id: "e414b44b-3be6-4dd7-9e03-9ac86265b662",
            type: "TEMPLATING",
            data: {
              label: "Templating Node",
              output_id: "b25e40da-e2ec-4cc3-b75e-07d9ddf4d33c",
              error_output_id: null,
              source_handle_id: "templating-source",
              target_handle_id: "templating-target",
              template_node_input_id: "20ef17f3-2d6f-43c6-bece-ee2e7a23ddde",
              output_type: "STRING",
            },
            inputs: [
              {
                id: "20ef17f3-2d6f-43c6-bece-ee2e7a23ddde",
                key: "template",
                value: {
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "{{ string }}",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
              {
                id: "af4c1c22-b82a-4f43-ae0f-be4be61e4a0c",
                key: "string",
                value: {
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "Hello, World!",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
            ],
            display_data: {
              position: {
                x: 254.0,
                y: 103.0,
              },
              z_index: 1,
              comment: {
                value: "Templates the input string using Jinja.",
                expanded: true,
              },
              width: 554.0,
              height: 290.0,
              icon: null,
              color: null,
            },
            base: null,
            definition: {
              name: "TemplatingNode",
              module: ["o2Xi6VWTNd1THb", "nodes", "templating_node"],
            },
            trigger: {
              id: "templating-target",
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            ports: [
              {
                id: "5a9d77e7-0f28-4e57-8f6f-3f96be444ed2",
                name: "default",
                type: "DEFAULT",
              },
            ],
            adornments: null,
            outputs: null,
            attributes: null,
          },
          {
            id: "b2439bcb-8dee-44b6-85f1-37f294b0e0cb",
            type: "TERMINAL",
            data: {
              label: "Output",
              name: "output",
              target_handle_id: "final-target",
              output_id: "99408c96-eb09-44ff-ab92-a8c362c13b6b",
              output_type: "STRING",
              node_input_id: "ca9f8d73-34df-41fd-8efc-16f11282e092",
            },
            inputs: [
              {
                id: "ca9f8d73-34df-41fd-8efc-16f11282e092",
                key: "node_input",
                value: {
                  rules: [
                    {
                      type: "NODE_OUTPUT",
                      data: {
                        node_id: "e414b44b-3be6-4dd7-9e03-9ac86265b662",
                        output_id: "b25e40da-e2ec-4cc3-b75e-07d9ddf4d33c",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
            ],
            display_data: {
              position: {
                x: 1622.0,
                y: 0.0,
              },
              z_index: 5,
              comment: {
                value: "Final output of the workflow.",
                expanded: true,
              },
              width: 522.0,
              height: 296.0,
              icon: null,
              color: null,
            },
            base: null,
            definition: {
              name: "Output",
              module: ["o2Xi6VWTNd1THb", "nodes", "output"],
            },
            trigger: {
              id: "final-target",
              merge_behavior: "AWAIT_ANY",
            },
            outputs: [
              {
                id: "99408c96-eb09-44ff-ab92-a8c362c13b6b",
                name: "value",
                type: "STRING",
                value: {
                  type: "NODE_OUTPUT",
                  node_id: "e414b44b-3be6-4dd7-9e03-9ac86265b662",
                  node_output_id: "b25e40da-e2ec-4cc3-b75e-07d9ddf4d33c",
                },
              },
            ],
          },
        ],
        edges: [
          {
            source_node_id: "9663d2e9-8e18-448b-b963-cac4539db9d7",
            source_handle_id: "entry_source",
            target_node_id: "4344baa3-cdfe-4c16-bb76-545e0f55dba9",
            target_handle_id: "generic-node-trigger",
            type: "DEFAULT",
            id: "edge_1",
          },
          {
            source_node_id: "4344baa3-cdfe-4c16-bb76-545e0f55dba9",
            source_handle_id: "generic-node-default-port",
            target_node_id: "e414b44b-3be6-4dd7-9e03-9ac86265b662",
            target_handle_id: "templating-target",
            type: "DEFAULT",
            id: "edge_2",
          },
        ],
      },
      input_variables: [],
      state_variables: [],
      output_variables: [],
      packages: [],
    };

    const project = new WorkflowProjectGenerator({
      absolutePathToOutputDirectory: tempDir,
      workflowVersionExecConfigData: displayData,
      moduleName: "code",
      vellumApiKey: "<TEST_API_KEY>",
    });

    await project.generateCode();

    const mapping = project.getNodeIdToFileMapping();
    expect(mapping).toEqual({
      "4344baa3-cdfe-4c16-bb76-545e0f55dba9": {
        name: "Generic Node",
        module: ["my_nodes", "my_custom_node"],
      },
      "e414b44b-3be6-4dd7-9e03-9ac86265b662": {
        name: "TemplatingNode",
        module: ["o2Xi6VWTNd1THb", "nodes", "templating_node"],
      },
      "b2439bcb-8dee-44b6-85f1-37f294b0e0cb": {
        name: "Output",
        module: ["o2Xi6VWTNd1THb", "nodes", "output"],
      },
    });
  });

  describe("generateCode", () => {
    const excludeFilesAtPaths: RegExp[] = [/\.pyc$/, /metadata\.json$/];
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
          join(tempDir, ...project.getModulePath()),
          excludeFilesAtPaths
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
  describe("generateCodeNodeDirectoryOnly", () => {
    const excludeFilesAtPaths: RegExp[] = [/\.pyc$/, /metadata\.json$/];
    const ignoreContentsOfFilesAtPaths: RegExp[] = [];

    it.each(
      getFixturesForProjectTest({
        includeFixtures: ["conditional_node_without_display"],
        fixtureMocks: {},
      })
    )(
      "should correctly generate code without display directory for fixture $fixtureName",
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
          join(tempDir, ...project.getModulePath()),
          excludeFilesAtPaths
        );
        const expectedFiles = getAllFilesInDir(codeDir, excludeFilesAtPaths);

        // Filter out display directory files from generated
        const generatedFilesNoDisplay = Object.fromEntries(
          Object.entries(generatedFiles).filter(
            ([path]) => !path.startsWith("display/") && path !== "__init__.py"
          )
        );
        const expectedFilesNoDisplay = Object.fromEntries(
          Object.entries(expectedFiles).filter(
            ([path]) => !path.startsWith("display/") && path !== "__init__.py"
          )
        );

        const extraFilePaths = difference(
          Object.keys(generatedFilesNoDisplay),
          Object.keys(expectedFilesNoDisplay)
        );
        const extraFiles = extraFilePaths.map(
          (path) => generatedFilesNoDisplay[path]
        );
        expect(extraFiles.length, `Found extra file(s): ${extraFiles}`).toBe(0);

        for (const [
          expectedRelativePath,
          expectedAbsolutePath,
        ] of Object.entries(expectedFilesNoDisplay)) {
          const generatedAbsolutePath =
            generatedFilesNoDisplay[expectedRelativePath];

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

    it("should generate metadata.json with node id to file mapping", async () => {
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
              id: "templating-node-id",
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
                          value: "Hello, World!",
                        },
                      },
                    ],
                  },
                },
              ],
              definition: {
                name: "TemplatingNode",
                module: ["code", "nodes", "templating_node"],
              },
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "templating-node-id",
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
      });

      await project.generateCode();

      const metadataPath = join(tempDir, "code", "metadata.json");
      expect(fs.existsSync(metadataPath)).toBe(true);

      const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
      expect(metadata.node_id_to_file_mapping).toEqual({
        "templating-node-id": {
          name: "TemplatingNode",
          module: ["code", "nodes", "templating_node"],
        },
      });
    });

    it("should generate metadata.json with trigger path to id mapping for scheduled trigger", async () => {
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
                    rules: [
                      {
                        type: "CONSTANT_VALUE",
                        data: {
                          type: "STRING",
                          value: "Hello, World!",
                        },
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              trigger: {
                id: "terminal_target",
                merge_behavior: "AWAIT_ANY",
              },
              outputs: [
                {
                  id: "terminal_output_id",
                  name: "value",
                  type: "STRING",
                },
              ],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "terminal-node",
              target_handle_id: "terminal_target",
              type: "DEFAULT",
              id: "edge_1",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        triggers: [
          {
            id: "trigger-1",
            type: "SCHEDULED",
            cron: "* * * * *",
            timezone: "UTC",
            attributes: [
              {
                id: "attribute-id-1",
                key: "attribute-1",
                type: "STRING",
              },
            ],
          },
        ],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      const metadataPath = join(tempDir, "code", "metadata.json");
      expect(fs.existsSync(metadataPath)).toBe(true);

      const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
      expect(metadata.trigger_path_to_id_mapping).toEqual({
        "code.triggers.scheduled.ScheduleTrigger": "trigger-1",
      });
    });

    it("should generate metadata.json with entrypoint and trigger edge id mappings (path-based keys)", async () => {
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
                    rules: [
                      {
                        type: "CONSTANT_VALUE",
                        data: {
                          type: "STRING",
                          value: "Hello, World!",
                        },
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              trigger: {
                id: "terminal_target",
                merge_behavior: "AWAIT_ANY",
              },
              outputs: [
                {
                  id: "terminal_output_id",
                  name: "value",
                  type: "STRING",
                },
              ],
            },
          ],
          edges: [
            {
              source_node_id: "entry",
              source_handle_id: "entry_source",
              target_node_id: "terminal-node",
              target_handle_id: "terminal_target",
              type: "DEFAULT",
              id: "edge_1",
            },
            {
              source_node_id: "trigger-1",
              source_handle_id: "trigger-1",
              target_node_id: "terminal-node",
              target_handle_id: "terminal_target",
              type: "DEFAULT",
              id: "edge_2",
            },
          ],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
        triggers: [
          {
            id: "trigger-1",
            type: "SCHEDULED",
            cron: "* * * * *",
            timezone: "UTC",
            attributes: [],
          },
        ],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      const metadataPath = join(tempDir, "code", "metadata.json");
      expect(fs.existsSync(metadataPath)).toBe(true);

      const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
      // Top-level entrypoint id should match UI id
      expect(metadata.entrypoint).toBe("entry");
      // ENTRYPOINT -> Node mapping uses "<entrypoint>|<target_node_path>"
      expect(metadata.entrypoint_edges_to_id).toEqual({
        "entry|code.nodes.final_output.FinalOutput": "edge_1",
      });
      // TRIGGER -> Node mapping uses "<trigger_path>|<target_node_path>"
      expect(metadata.trigger_edges_to_id).toEqual({
        "code.triggers.scheduled.ScheduleTrigger|code.nodes.final_output.FinalOutput": "edge_2",
      });
    });
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
        strict: true,
      });

      expect(project.generateCode()).rejects.toThrow(
        new NodeAttributeGenerationError(
          "Failed to generate attribute 'BadNode.inputs.other': Failed to find node with id 'node_that_doesnt_exist'"
        )
      );
    });

    it("should create output directory even when generateAssets fails", async () => {
      /**
       * Tests that the module directory is created even when generateAssets() throws an error.
       * This prevents 500 errors in the codegen service when asset generation fails.
       */

      // GIVEN a minimal workflow configuration
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
          ],
          edges: [],
        },
        input_variables: [],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "test_module",
        vellumApiKey: "<TEST_API_KEY>",
      });

      vi.spyOn(
        project as unknown as { generateAssets: () => Promise<unknown> },
        "generateAssets"
      ).mockRejectedValue(new Error("Asset generation failed"));

      await project.generateCode();

      expectProjectFileToExist(["test_module"]);

      const moduleDir = join(tempDir, "test_module");
      const files = await readdir(moduleDir).catch(() => []);
      expect(files.filter((f: string) => f.endsWith(".py")).length).toBe(0);
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
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "bad_node.py"]);
    });

    it("should generate code even if createNodeContext throws an error for one node", async () => {
      /**
       * Tests that workflow generation continues even when createNodeContext fails for individual nodes.
       * This reproduces the issue where a single node failure would cause entire workflow failure.
       */

      // GIVEN a workflow with two templating nodes
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
              id: "templating-node-1",
              type: "TEMPLATING",
              data: {
                label: "First Node",
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
                          value: "Hello World",
                        },
                      },
                    ],
                  },
                },
              ],
            },
            {
              id: "templating-node-2",
              type: "TEMPLATING",
              data: {
                label: "Second Node",
                template_node_input_id: "template",
                output_id: "output",
                output_type: "STRING",
                source_handle_id: "template_source_2",
                target_handle_id: "template_target_2",
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
                          value: "Hello Again",
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
              target_node_id: "templating-node-1",
              target_handle_id: "template_target_1",
              type: "DEFAULT",
              id: "edge_1",
            },
            {
              source_node_id: "templating-node-1",
              source_handle_id: "template_source_1",
              target_node_id: "templating-node-2",
              target_handle_id: "template_target_2",
              type: "DEFAULT",
              id: "edge_2",
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
      });

      const contextModule = await import("src/context");
      let callCount = 0;
      const originalCreateNodeContext = contextModule.createNodeContext;

      const mockCreateNodeContext = vi.fn().mockImplementation((args) => {
        callCount++;
        if (callCount === 2) {
          throw new Error("Mocked createNodeContext failure");
        }
        return originalCreateNodeContext(args);
      });

      vi.spyOn(contextModule, "createNodeContext").mockImplementation(
        mockCreateNodeContext
      );

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);

      // AND only the successful node should be generated (first templating node)
      expectProjectFileToExist(["code", "nodes", "first_node.py"]);

      expect(() =>
        expectProjectFileToExist(["code", "nodes", "second_node.py"])
      ).toThrow();

      const errors = project.workflowContext.getErrors();
      expect(errors.length).toBeGreaterThan(0);
      expect(
        errors.some((error) =>
          error.message.includes("Failed to create node context")
        )
      ).toBe(true);
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
        strict: true,
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "final_output.py"]);
    });
  });

  describe("Nodes present but not in graph", () => {
    const firstNodeId = uuidv4();
    const secondNodeId = "6bdede82-bcd6-42ab-8f6b-b3988fc6648f";
    const secondNodeOutputId = "bd71c32b-0762-4556-a1bc-2c36b15f6428";
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
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "nodes", "prompt.py"]);
      expectProjectFileToExist(["code", "display", "nodes", "prompt.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "prompt.py"]);
      expectProjectFileToMatchSnapshot([
        "code",
        "display",
        "nodes",
        "prompt.py",
      ]);
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
              trigger: null,
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
              trigger: null,
              definition: {
                name: "TryNode",
                module: [
                  "code",
                  "nodes",
                  "prompt",
                  "Prompt",
                  "<adornment>",
                  "RetryNode",
                  "<adornment>",
                ],
              },
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
              trigger: null,
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
      });

      await project.generateCode();
      expectProjectFileToExist(["code", "nodes", "templating_node.py"]);
      expectProjectFileToMatchSnapshot(["code", "nodes", "templating_node.py"]);
    });
  });
  describe("Get generic node files", () => {
    it.each([
      { moduleName: "generic_test" },
      { moduleName: "my.generic.test" },
    ])("should get generic node files", async ({ moduleName }) => {
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
        moduleName,
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
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
                  "displayable",
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
              trigger: null,
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
              trigger: null,
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
              trigger: null,
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
              trigger: null,
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
              trigger: null,
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
              trigger: null,
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
              trigger: null,
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
                  "displayable",
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
                          type: "CODE_EXECUTION",
                          src: 'def get_current_weather(location: str, unit: str) -> str:\n    """\n    Get the current weather in a given location.\n    """\n    return f"The current weather in {location} is sunny with a temperature of 70 degrees {unit}."\n',
                          name: "get_current_weather",
                          description:
                            "Get the current weather in a given location.",
                          definition: {
                            name: "get_current_weather",
                            state: null,
                            forced: null,
                            strict: null,
                            inputs: {
                              location: {
                                type: "WORKFLOW_INPUT",
                                input_variable_id:
                                  "4bf1f0e7-76c6-4204-9f8c-bd9c3b73a8db",
                              },
                            },
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
                          type: "CODE_EXECUTION",
                          src: `def format_answer(answer: str) -> str:\n    """\n    Format the answer and request the LLM to provide a final text summary.\n    """\n    formatted = f"The answer to the question is: {answer}"\n    return (\n        f"{formatted}\\n\\nNow please provide a final summary with any temperature conversions or additional information."\n    )\n`,
                          name: "format_answer",
                          description:
                            "Format the answer and request the LLM to provide a final text summary.",
                          definition: {
                            name: "format_answer",
                            state: null,
                            forced: null,
                            strict: null,
                            inputs: null,
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
        input_variables: [
          {
            id: "4bf1f0e7-76c6-4204-9f8c-bd9c3b73a8db",
            key: "location",
            type: "STRING",
          },
        ],
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
      expectProjectFileToMatchSnapshot(["code", "nodes", "__init__.py"]);
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "tool_call",
        "__init__.py",
      ]);
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "tool_call",
        "get_current_weather.py",
      ]);
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "tool_call",
        "format_answer.py",
      ]);
      expectProjectFileToMatchSnapshot([
        "code",
        "display",
        "nodes",
        "tool_call",
        "__init__.py",
      ]);
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
                  "displayable",
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
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "tool_call",
        "__init__.py",
      ]);
    });

    it("should not generate redundant Outputs class for ToolCallingNode with default outputs", async () => {
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
                  "displayable",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "SimpleToolCallingNode",
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
                                  text: "You are a helpful assistant",
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
              ],
              definition: {
                name: "SimpleToolCallingNode",
                module: ["testing", "nodes", "simple_tool_call"],
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
      });

      await project.generateCode();

      const generatedFilePath = join(
        tempDir,
        "code",
        "nodes",
        "simple_tool_call",
        "__init__.py"
      );
      const generatedContent = fs.readFileSync(generatedFilePath, "utf-8");

      expect(generatedContent).not.toContain(
        "class Outputs(ToolCallingNode.Outputs):"
      );
    });

    it.each([
      { name: "no packages", packages: [] },
      {
        name: "with packages",
        packages: [{ name: "requests", version: "2.32.3" }],
      },
    ])("should generate inline workflow tool $name", async ({ packages }) => {
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              id: "3957f0e7-d95b-4571-8587-ab05cb65d815",
              type: "DEFAULT",
              source_node_id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
              target_node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
              source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
              target_handle_id: "2414743b-b1dd-4552-8abf-9b7481df9762",
            },
            {
              id: "c5d9c2ec-e794-4c1a-9f81-90dba294c90d",
              type: "DEFAULT",
              source_node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
              target_node_id: "2c368766-015e-4d2f-8f57-01937038a4b2",
              source_handle_id: "3cd6d78c-9dad-42aa-ad38-31f67057c379",
              target_handle_id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
            },
            {
              id: "6a6ac98a-faf5-4ddf-aac1-4bfec7b69e24",
              type: "DEFAULT",
              source_node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
              target_node_id: "88e59503-f7fb-48cc-b535-3cd1db07627a",
              source_handle_id: "3cd6d78c-9dad-42aa-ad38-31f67057c379",
              target_handle_id: "645fee43-832a-4622-89fd-b2ead42a2ec0",
            },
            {
              id: "de285875-d306-4b45-87b5-1c9fc4123f8c",
              type: "DEFAULT",
              source_node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
              target_node_id: "8834dd6c-d3cc-49fa-aec8-6a6d23ca2d6a",
              source_handle_id: "3cd6d78c-9dad-42aa-ad38-31f67057c379",
              target_handle_id: "0e22c690-31a4-4e70-b0ad-c351e862d644",
            },
          ],
          nodes: [
            {
              id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
              display_data: {
                width: null,
                height: null,
                comment: null,
                position: { x: 0.0, y: 0.0 },
              },
            },
            {
              id: "21f29cac-da87-495f-bba1-093d423f4e46",
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "GetCurrentWeatherNode",
              ports: [
                {
                  id: "3cd6d78c-9dad-42aa-ad38-31f67057c379",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "e62bc785-a914-4066-b79e-8c89a5d0ec6c",
                  name: "text",
                  type: "STRING",
                  value: null,
                },
                {
                  id: "4674f1d9-e3af-411f-8a55-40a3a3ab5394",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: null,
                },
              ],
              trigger: {
                id: "2414743b-b1dd-4552-8abf-9b7481df9762",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [
                {
                  id: "44420e39-966f-4c59-bdf8-6365a61c5d2a",
                  name: "ml_model",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "gpt-4o-mini" },
                  },
                },
                {
                  id: "5c041b7d-732c-4773-a93a-32211f2af0b3",
                  name: "max_tool_calls",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "NUMBER", value: 3.0 },
                  },
                },
                {
                  id: "669cfb4b-8c25-460e-8952-b63d91302cbc",
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
                                  text: "What is the weather in ",
                                  state: null,
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
                                },
                                {
                                  state: null,
                                  block_type: "VARIABLE",
                                  cache_config: null,
                                  input_variable: "city",
                                },
                                {
                                  text: " on ",
                                  state: null,
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
                                },
                                {
                                  state: null,
                                  block_type: "VARIABLE",
                                  cache_config: null,
                                  input_variable: "date",
                                },
                                {
                                  text: "?",
                                  state: null,
                                  block_type: "PLAIN_TEXT",
                                  cache_config: null,
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
                  id: "78324739-ff89-47a5-902b-10da0cb95c6d",
                  name: "functions",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          type: "INLINE_WORKFLOW",
                          description:
                            "Test description for inline workflow tool",
                          exec_config: {
                            input_variables: [
                              {
                                id: "5246e023-8bcb-4572-be8e-ca9cf19807da",
                                key: "city",
                                type: "STRING",
                                default: null,
                                required: true,
                                extensions: { color: null },
                              },
                              {
                                id: "c5d2aa82-10ad-4511-97ce-66b01af721a1",
                                key: "date",
                                type: "STRING",
                                default: null,
                                required: true,
                                extensions: { color: null },
                              },
                            ],
                            state_variables: [],
                            output_variables: [
                              {
                                id: "1f300ab1-7a63-4c0f-81d5-5e6df2a5181c",
                                key: "temperature",
                                type: "NUMBER",
                              },
                              {
                                id: "64c803c9-02a0-4133-8858-14a3bddc0600",
                                key: "reasoning",
                                type: "STRING",
                              },
                            ],
                            workflow_raw_data: {
                              edges: [
                                {
                                  id: "15b49a1f-c033-4f50-a12f-42daae03539e",
                                  type: "DEFAULT",
                                  source_node_id:
                                    "d97d2a36-3347-487e-b915-3bc874aaded4",
                                  target_node_id: "code-execution-node-id",
                                  source_handle_id:
                                    "c55f8e1e-0422-4009-af54-86df5625ba71",
                                  target_handle_id:
                                    "3400f8bc-ed0a-4029-8a52-038e1bc4cb93",
                                },
                                {
                                  id: "code-to-start-edge",
                                  type: "DEFAULT",
                                  source_node_id: "code-execution-node-id",
                                  target_node_id: "start-node-id",
                                  source_handle_id:
                                    "5352eb9f-c28f-4e90-b32e-82cb970efa21",
                                  target_handle_id:
                                    "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                },
                                {
                                  id: "ab8c4a64-465d-4406-a407-9faa09d0326d",
                                  type: "DEFAULT",
                                  source_node_id: "start-node-id",
                                  target_node_id:
                                    "938ac916-6b4d-4097-a16e-cf7feb663b17",
                                  source_handle_id:
                                    "1e739e86-a285-4438-9725-a152c15a63e3",
                                  target_handle_id:
                                    "332d152e-1648-42a0-a35a-03f2e71a5752",
                                },
                                {
                                  id: "f9dc12de-4284-419d-beb2-927452b80da0",
                                  type: "DEFAULT",
                                  source_node_id: "start-node-id",
                                  target_node_id:
                                    "d4abe0fd-0ba5-438c-8d20-4155ca89429e",
                                  source_handle_id:
                                    "1e739e86-a285-4438-9725-a152c15a63e3",
                                  target_handle_id:
                                    "7b3a550b-9b15-4707-8457-856976be003a",
                                },
                              ],
                              nodes: [
                                {
                                  id: "d97d2a36-3347-487e-b915-3bc874aaded4",
                                  base: null,
                                  data: {
                                    label: "Entrypoint Node",
                                    source_handle_id:
                                      "c55f8e1e-0422-4009-af54-86df5625ba71",
                                  },
                                  type: "ENTRYPOINT",
                                  inputs: [],
                                  definition: null,
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                                {
                                  id: "code-execution-node-id",
                                  data: {
                                    label: "Code Execution Node",
                                    filepath: null,
                                    packages,
                                    output_id:
                                      "f2ea61aa-256e-41b0-8ab4-aa3a22e489dd",
                                    output_type: "NUMBER",
                                    code_input_id:
                                      "82a5d32f-fc12-4b64-b72c-2a65f860f8cb",
                                    log_output_id:
                                      "77eab8ac-bc36-4f53-8449-8be6396d3331",
                                    error_output_id: null,
                                    runtime_input_id:
                                      "247da47f-ad5b-412d-825a-61c29c6a3847",
                                    source_handle_id:
                                      "5352eb9f-c28f-4e90-b32e-82cb970efa21",
                                    target_handle_id:
                                      "3400f8bc-ed0a-4029-8a52-038e1bc4cb93",
                                  },
                                  type: "CODE_EXECUTION",
                                  ports: [
                                    {
                                      id: "5352eb9f-c28f-4e90-b32e-82cb970efa21",
                                      name: "default",
                                      type: "DEFAULT",
                                    },
                                  ],
                                  inputs: [
                                    {
                                      id: "82a5d32f-fc12-4b64-b72c-2a65f860f8cb",
                                      key: "code",
                                      value: {
                                        rules: [
                                          {
                                            data: {
                                              type: "STRING",
                                              value:
                                                "def main(\n    arg1: int,\n    arg2: int,\n) -> int:\n    return arg1 + arg2\n    ",
                                            },
                                            type: "CONSTANT_VALUE",
                                          },
                                        ],
                                        combinator: "OR",
                                      },
                                    },
                                    {
                                      id: "247da47f-ad5b-412d-825a-61c29c6a3847",
                                      key: "runtime",
                                      value: {
                                        rules: [
                                          {
                                            data: {
                                              type: "STRING",
                                              value: "PYTHON_3_11_6",
                                            },
                                            type: "CONSTANT_VALUE",
                                          },
                                        ],
                                        combinator: "OR",
                                      },
                                    },
                                  ],
                                  trigger: {
                                    id: "3400f8bc-ed0a-4029-8a52-038e1bc4cb93",
                                    merge_behavior: "AWAIT_ANY",
                                  },
                                },
                                {
                                  id: "start-node-id",
                                  base: {
                                    name: "BaseNode",
                                    module: [
                                      "vellum",
                                      "workflows",
                                      "nodes",
                                      "bases",
                                      "base",
                                    ],
                                  },
                                  type: "GENERIC",
                                  label: "StartNode",
                                  ports: [
                                    {
                                      id: "1e739e86-a285-4438-9725-a152c15a63e3",
                                      name: "default",
                                      type: "DEFAULT",
                                    },
                                  ],
                                  outputs: [
                                    {
                                      id: "3f4c753e-f057-47bb-9748-7968283cc8aa",
                                      name: "temperature",
                                      type: "NUMBER",
                                      value: null,
                                    },
                                    {
                                      id: "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",
                                      name: "reasoning",
                                      type: "STRING",
                                      value: null,
                                    },
                                  ],
                                  trigger: {
                                    id: "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                    merge_behavior: "AWAIT_ATTRIBUTES",
                                  },
                                  adornments: null,
                                  attributes: [
                                    {
                                      id: "60ad78cd-fc78-4e08-926d-5a095b34d4f5",
                                      name: "city",
                                      value: {
                                        type: "WORKFLOW_INPUT",
                                        input_variable_id:
                                          "5246e023-8bcb-4572-be8e-ca9cf19807da",
                                      },
                                    },
                                    {
                                      id: "c5f2d66c-5bb6-4d2a-8e4d-5356318cd3ba",
                                      name: "date",
                                      value: {
                                        type: "WORKFLOW_INPUT",
                                        input_variable_id:
                                          "c5d2aa82-10ad-4511-97ce-66b01af721a1",
                                      },
                                    },
                                  ],
                                  definition: {
                                    name: "StartNode",
                                    module: [
                                      "local_inline_subworkflow",
                                      "nodes",
                                      "tool_call_start_node",
                                    ],
                                  },
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                                {
                                  id: "938ac916-6b4d-4097-a16e-cf7feb663b17",
                                  base: {
                                    name: "FinalOutputNode",
                                    module: [
                                      "vellum",
                                      "workflows",
                                      "nodes",
                                      "displayable",
                                      "final_output_node",
                                      "node",
                                    ],
                                  },
                                  data: {
                                    name: "temperature",
                                    label: "Final Output",
                                    output_id:
                                      "1f300ab1-7a63-4c0f-81d5-5e6df2a5181c",
                                    output_type: "NUMBER",
                                    node_input_id:
                                      "fdb9bc1c-b556-4b75-848d-93082b472ecf",
                                    target_handle_id:
                                      "332d152e-1648-42a0-a35a-03f2e71a5752",
                                  },
                                  type: "TERMINAL",
                                  inputs: [
                                    {
                                      id: "fdb9bc1c-b556-4b75-848d-93082b472ecf",
                                      key: "node_input",
                                      value: {
                                        rules: [
                                          {
                                            data: {
                                              node_id: "start-node-id",
                                              output_id:
                                                "3f4c753e-f057-47bb-9748-7968283cc8aa",
                                            },
                                            type: "NODE_OUTPUT",
                                          },
                                        ],
                                        combinator: "OR",
                                      },
                                    },
                                  ],
                                  definition: null,
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                                {
                                  id: "d4abe0fd-0ba5-438c-8d20-4155ca89429e",
                                  base: {
                                    name: "FinalOutputNode",
                                    module: [
                                      "vellum",
                                      "workflows",
                                      "nodes",
                                      "displayable",
                                      "final_output_node",
                                      "node",
                                    ],
                                  },
                                  data: {
                                    name: "reasoning",
                                    label: "Final Output",
                                    output_id:
                                      "64c803c9-02a0-4133-8858-14a3bddc0600",
                                    output_type: "STRING",
                                    node_input_id:
                                      "c91758da-fe9c-460c-b7d4-6c550750e46c",
                                    target_handle_id:
                                      "7b3a550b-9b15-4707-8457-856976be003a",
                                  },
                                  type: "TERMINAL",
                                  inputs: [
                                    {
                                      id: "c91758da-fe9c-460c-b7d4-6c550750e46c",
                                      key: "node_input",
                                      value: {
                                        rules: [
                                          {
                                            data: {
                                              node_id: "start-node-id",
                                              output_id:
                                                "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",
                                            },
                                            type: "NODE_OUTPUT",
                                          },
                                        ],
                                        combinator: "OR",
                                      },
                                    },
                                  ],
                                  definition: null,
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                              ],
                              definition: {
                                name: "WeatherFunction",
                                module: [
                                  "local_inline_subworkflow",
                                  "nodes",
                                  "tool_call_weather_function",
                                ],
                              },
                              display_data: {
                                viewport: { x: 0.0, y: 0.0, zoom: 1.0 },
                              },
                              output_values: [
                                {
                                  value: {
                                    type: "NODE_OUTPUT",
                                    node_id:
                                      "938ac916-6b4d-4097-a16e-cf7feb663b17",
                                    node_output_id:
                                      "1f300ab1-7a63-4c0f-81d5-5e6df2a5181c",
                                  },
                                  output_variable_id:
                                    "1f300ab1-7a63-4c0f-81d5-5e6df2a5181c",
                                },
                                {
                                  value: {
                                    type: "NODE_OUTPUT",
                                    node_id:
                                      "d4abe0fd-0ba5-438c-8d20-4155ca89429e",
                                    node_output_id:
                                      "64c803c9-02a0-4133-8858-14a3bddc0600",
                                  },
                                  output_variable_id:
                                    "64c803c9-02a0-4133-8858-14a3bddc0600",
                                },
                              ],
                            },
                          },
                        },
                      ],
                    },
                  },
                },
                {
                  id: "0f6dc102-3460-4963-91fa-7ba85d65ef7a",
                  name: "prompt_inputs",
                  value: {
                    type: "DICTIONARY_REFERENCE",
                    entries: [
                      {
                        id: "0b1fe7d3-e746-4793-a6e8-2cd1a518c6f9",
                        key: "city",
                        value: {
                          type: "WORKFLOW_INPUT",
                          input_variable_id:
                            "aff59ccd-dcbd-49fa-9ede-a38f0bf9cfc6",
                        },
                      },
                      {
                        id: "1f5ba43b-49e0-484e-acc5-f29f1b8cc7ab",
                        key: "date",
                        value: {
                          type: "WORKFLOW_INPUT",
                          input_variable_id:
                            "7e8dc92c-a6bf-48c3-b182-6edf2515ed67",
                        },
                      },
                    ],
                  },
                },
              ],
              definition: {
                name: "GetCurrentWeatherNode",
                module: [
                  "local_inline_subworkflow",
                  "nodes",
                  "tool_call_get_current_weather_node",
                ],
              },
              display_data: {
                comment: {
                  value:
                    "\n    A tool calling node that calls the get_current_weather function.\n    ",
                  expanded: false,
                },
                position: { x: 0.0, y: 0.0 },
              },
            },
            {
              id: "2c368766-015e-4d2f-8f57-01937038a4b2",
              base: {
                name: "FinalOutputNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "final_output_node",
                  "node",
                ],
              },
              data: {
                name: "final_output",
                label: "Final Output",
                output_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
                output_type: "STRING",
                node_input_id: "287431be-000d-498d-9dd0-b8dddbce5a5a",
                target_handle_id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
              },
              type: "TERMINAL",
              inputs: [
                {
                  id: "287431be-000d-498d-9dd0-b8dddbce5a5a",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        data: {
                          input_variable_id:
                            "aff59ccd-dcbd-49fa-9ede-a38f0bf9cfc6",
                        },
                        type: "INPUT_VARIABLE",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              outputs: [
                {
                  id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
                  name: "value",
                  type: "STRING",
                  value: {
                    type: "WORKFLOW_INPUT",
                    input_variable_id: "aff59ccd-dcbd-49fa-9ede-a38f0bf9cfc6",
                  },
                },
              ],
              trigger: {
                id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
                merge_behavior: "AWAIT_ANY",
              },
              definition: {
                name: "FinalOutput",
                module: ["local_inline_subworkflow", "nodes", "final_output"],
              },
              display_data: {
                width: null,
                height: null,
                comment: null,
                position: { x: 0.0, y: 0.0 },
              },
            },
            {
              id: "88e59503-f7fb-48cc-b535-3cd1db07627a",
              base: {
                name: "FinalOutputNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "final_output_node",
                  "node",
                ],
              },
              data: {
                name: "text",
                label: "Final Output",
                output_id: "9a233225-16ef-48b4-8cf6-d8a6c1ae72ce",
                output_type: "STRING",
                node_input_id: "a622d76c-6cc3-4353-8d09-ca4cdaf0dc1c",
                target_handle_id: "645fee43-832a-4622-89fd-b2ead42a2ec0",
              },
              type: "TERMINAL",
              inputs: [
                {
                  id: "a622d76c-6cc3-4353-8d09-ca4cdaf0dc1c",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        data: {
                          node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
                          output_id: "e62bc785-a914-4066-b79e-8c89a5d0ec6c",
                        },
                        type: "NODE_OUTPUT",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              outputs: [
                {
                  id: "9a233225-16ef-48b4-8cf6-d8a6c1ae72ce",
                  name: "value",
                  type: "STRING",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
                    node_output_id: "e62bc785-a914-4066-b79e-8c89a5d0ec6c",
                  },
                },
              ],
              trigger: {
                id: "645fee43-832a-4622-89fd-b2ead42a2ec0",
                merge_behavior: "AWAIT_ANY",
              },
              definition: null,
              display_data: {
                width: null,
                height: null,
                comment: null,
                position: { x: 0.0, y: 0.0 },
              },
            },
            {
              id: "8834dd6c-d3cc-49fa-aec8-6a6d23ca2d6a",
              base: {
                name: "FinalOutputNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "final_output_node",
                  "node",
                ],
              },
              data: {
                name: "chat_history",
                label: "Final Output",
                output_id: "5ebf2c00-cb24-421b-9a23-5e0e2673f1ef",
                output_type: "CHAT_HISTORY",
                node_input_id: "e52e08eb-28fc-44ef-b61b-2ab273413592",
                target_handle_id: "0e22c690-31a4-4e70-b0ad-c351e862d644",
              },
              type: "TERMINAL",
              inputs: [
                {
                  id: "e52e08eb-28fc-44ef-b61b-2ab273413592",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        data: {
                          node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
                          output_id: "4674f1d9-e3af-411f-8a55-40a3a3ab5394",
                        },
                        type: "NODE_OUTPUT",
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              outputs: [
                {
                  id: "5ebf2c00-cb24-421b-9a23-5e0e2673f1ef",
                  name: "value",
                  type: "CHAT_HISTORY",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "21f29cac-da87-495f-bba1-093d423f4e46",
                    node_output_id: "4674f1d9-e3af-411f-8a55-40a3a3ab5394",
                  },
                },
              ],
              trigger: {
                id: "0e22c690-31a4-4e70-b0ad-c351e862d644",
                merge_behavior: "AWAIT_ANY",
              },
              definition: null,
              display_data: {
                width: null,
                height: null,
                comment: null,
                position: { x: 0.0, y: 0.0 },
              },
            },
          ],
          definition: {
            name: "Workflow",
            module: ["local_inline_subworkflow", "workflow"],
          },
          display_data: { viewport: { x: 0.0, y: 0.0, zoom: 1.0 } },
          output_values: [
            {
              value: {
                type: "NODE_OUTPUT",
                node_id: "2c368766-015e-4d2f-8f57-01937038a4b2",
                node_output_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
              },
              output_variable_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
            },
            {
              value: {
                type: "NODE_OUTPUT",
                node_id: "88e59503-f7fb-48cc-b535-3cd1db07627a",
                node_output_id: "9a233225-16ef-48b4-8cf6-d8a6c1ae72ce",
              },
              output_variable_id: "dbedc4ee-be3b-4135-8c26-3643c0b6a530",
            },
            {
              value: {
                type: "NODE_OUTPUT",
                node_id: "8834dd6c-d3cc-49fa-aec8-6a6d23ca2d6a",
                node_output_id: "5ebf2c00-cb24-421b-9a23-5e0e2673f1ef",
              },
              output_variable_id: "c5733df5-03bb-498e-a770-8ef9bff85df3",
            },
          ],
        },
        input_variables: [
          {
            id: "045942b7-e5b9-482c-b4d4-943309a20e05",
            key: "query",
            type: "STRING",
            default: null,
            required: true,
            extensions: { color: null },
          },
          {
            id: "aff59ccd-dcbd-49fa-9ede-a38f0bf9cfc6",
            key: "city",
            type: "STRING",
            default: null,
            required: true,
          },
          {
            id: "7e8dc92c-a6bf-48c3-b182-6edf2515ed67",
            key: "date",
            type: "STRING",
            default: null,
            required: true,
          },
        ],
        state_variables: [],
        output_variables: [
          {
            id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
            key: "final_output",
            type: "STRING",
          },
          {
            id: "dbedc4ee-be3b-4135-8c26-3643c0b6a530",
            key: "text",
            type: "STRING",
          },
          {
            id: "c5733df5-03bb-498e-a770-8ef9bff85df3",
            key: "chat_history",
            type: "CHAT_HISTORY",
          },
        ],
      };
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });
      await project.generateCode();

      expect(project.workflowContext.getErrors()).toHaveLength(0);
      const expectedFiles = [
        ["code", "inputs.py"],
        ["code", "nodes", "__init__.py"],
        ["code", "nodes", "final_output.py"],
        ["code", "nodes", "final_output_1.py"],
        ["code", "nodes", "final_output_2.py"],
        ["code", "nodes", "tool_call_get_current_weather_node", "__init__.py"],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "__init__.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "inputs.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "nodes",
          "__init__.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "nodes",
          "final_output.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "nodes",
          "final_output_1.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "nodes",
          "tool_call_start_node.py",
        ],
        [
          "code",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "workflow.py",
        ],
        ["code", "workflow.py"],
        [
          "code",
          "display",
          "nodes",
          "tool_call_get_current_weather_node",
          "__init__.py",
        ],
        [
          "code",
          "display",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "nodes",
          "__init__.py",
        ],
        [
          "code",
          "display",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "workflow.py",
        ],
        [
          "code",
          "display",
          "nodes",
          "tool_call_get_current_weather_node",
          "weather_function",
          "__init__.py",
        ],
      ];

      for (const file of expectedFiles) {
        expectProjectFileToMatchSnapshot(file);
      }
    });
    it("should not generate docstring if description is empty string", async () => {
      const displayData = {
        workflow_raw_data: {
          edges: [],
          nodes: [
            {
              id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
              base: null,
              data: {
                label: "Entrypoint Node",
                source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
              },
              type: "ENTRYPOINT",
              inputs: [],
              definition: null,
              display_data: {
                width: null,
                height: null,
                comment: null,
                position: { x: 0.0, y: 0.0 },
              },
            },
            {
              id: "21f29cac-da87-495f-bba1-093d423f4e46",
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "tool_calling_node",
                  "node",
                ],
              },
              type: "GENERIC",
              label: "GetCurrentWeatherNode",
              ports: [],
              outputs: [],
              trigger: {
                id: "2414743b-b1dd-4552-8abf-9b7481df9762",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [
                {
                  id: "78324739-ff89-47a5-902b-10da0cb95c6d",
                  name: "functions",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          type: "INLINE_WORKFLOW",
                          description: "", // empty string
                          exec_config: {
                            input_variables: [
                              {
                                id: "5246e023-8bcb-4572-be8e-ca9cf19807da",
                                key: "city",
                                type: "STRING",
                                default: null,
                                required: true,
                                extensions: { color: null },
                              },
                              {
                                id: "c5d2aa82-10ad-4511-97ce-66b01af721a1",
                                key: "date",
                                type: "STRING",
                                default: null,
                                required: true,
                                extensions: { color: null },
                              },
                            ],
                            state_variables: [],
                            output_variables: [],
                            workflow_raw_data: {
                              edges: [
                                {
                                  id: "15b49a1f-c033-4f50-a12f-42daae03539e",
                                  type: "DEFAULT",
                                  source_node_id:
                                    "d97d2a36-3347-487e-b915-3bc874aaded4",
                                  target_node_id: "start-node-id",
                                  source_handle_id:
                                    "c55f8e1e-0422-4009-af54-86df5625ba71",
                                  target_handle_id:
                                    "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                },
                              ],
                              nodes: [
                                {
                                  id: "d97d2a36-3347-487e-b915-3bc874aaded4",
                                  base: null,
                                  data: {
                                    label: "Entrypoint Node",
                                    source_handle_id:
                                      "c55f8e1e-0422-4009-af54-86df5625ba71",
                                  },
                                  type: "ENTRYPOINT",
                                  inputs: [],
                                  definition: null,
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                                {
                                  id: "start-node-id",
                                  base: {
                                    name: "BaseNode",
                                    module: [
                                      "vellum",
                                      "workflows",
                                      "nodes",
                                      "bases",
                                      "base",
                                    ],
                                  },
                                  type: "GENERIC",
                                  label: "StartNode",
                                  ports: [
                                    {
                                      id: "1e739e86-a285-4438-9725-a152c15a63e3",
                                      name: "default",
                                      type: "DEFAULT",
                                    },
                                  ],
                                  outputs: [],
                                  trigger: {
                                    id: "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                    merge_behavior: "AWAIT_ATTRIBUTES",
                                  },
                                  adornments: null,
                                  attributes: [],
                                  definition: {
                                    name: "StartNode",
                                    module: [
                                      "local_inline_subworkflow",
                                      "nodes",
                                      "tool_call_start_node",
                                    ],
                                  },
                                  display_data: {
                                    position: { x: 0.0, y: 0.0 },
                                  },
                                },
                              ],
                              definition: {
                                name: "WeatherFunction",
                                module: [
                                  "local_inline_subworkflow",
                                  "nodes",
                                  "tool_call_weather_function",
                                ],
                              },
                              display_data: {
                                viewport: { x: 0.0, y: 0.0, zoom: 1.0 },
                              },
                              output_values: [],
                            },
                          },
                        },
                      ],
                    },
                  },
                },
              ],
              definition: {
                name: "GetCurrentWeatherNode",
                module: [
                  "local_inline_subworkflow",
                  "nodes",
                  "tool_call_get_current_weather_node",
                ],
              },
              display_data: {},
            },
          ],
          definition: {
            name: "Workflow",
            module: ["local_inline_subworkflow", "workflow"],
          },
          display_data: { viewport: { x: 0.0, y: 0.0, zoom: 1.0 } },
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
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "tool_call_get_current_weather_node",
        "weather_function",
        "workflow.py",
      ]);
    });
    it("should generate workflow deployment tool", async () => {
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
              id: "b6d28aed-a60f-4c29-9d02-6a130358f2be",
              label: "MyToolCallingNode",
              type: "GENERIC",
              display_data: { position: { x: 0.0, y: 0.0 } },
              base: {
                name: "ToolCallingNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "tool_calling_node",
                  "node",
                ],
              },
              definition: {
                name: "MyToolCallingNode",
                module: [
                  "tests",
                  "workflows",
                  "basic_tool_calling_node_workflow_deployment",
                  "workflow",
                ],
              },
              trigger: {
                id: "e7774637-d160-4c4a-8106-4fa15b261f5f",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: "9427ace6-cc30-4c4c-ac09-91842e6ca01f",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              adornments: null,
              attributes: [
                {
                  id: "43a479ed-8130-403b-b6d4-e085bab497db",
                  name: "ml_model",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "gpt-4" },
                  },
                },
                {
                  id: "f17c7e76-5696-485f-92a7-45dfc94b10fb",
                  name: "blocks",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [],
                    },
                  },
                },
                {
                  id: "73a94e3c-1935-4308-a68a-ecd5441804b7",
                  name: "functions",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "JSON",
                      value: [
                        {
                          name: "add_code_exec",
                          type: "WORKFLOW_DEPLOYMENT",
                          deployment: "add-code-exec",
                          description: "",
                          release_tag: "LATEST",
                        },
                      ],
                    },
                  },
                },
                {
                  id: "f8ef2b4f-4c43-4d24-84b1-63081e5fc490",
                  name: "prompt_inputs",
                  value: {
                    type: "DICTIONARY_REFERENCE",
                    entries: [],
                  },
                },
              ],
              outputs: [
                {
                  id: "de0286f1-d33f-4953-9808-3aa8330af2d6",
                  name: "text",
                  type: "STRING",
                  value: null,
                },
                {
                  id: "77bc809c-4d17-4e61-ac7d-93da4d17a40f",
                  name: "chat_history",
                  type: "CHAT_HISTORY",
                  value: null,
                },
              ],
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
      });

      await project.generateCode();
      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "workflow",
        "__init__.py",
      ]);
    });
  });

  it("should generate correct tool calling init file with multi-level module path", async () => {
    const displayData = {
      workflow_raw_data: {
        edges: [
          {
            type: "DEFAULT",
            id: "9332ff7d-1047-40b2-952a-d1083fac59d6",
            source_node_id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
            source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
            target_node_id: "035842e0-34ed-43af-97de-a706e40912ae",
            target_handle_id: "f9b4a4ce-68ae-45f4-9e29-38b588abdf97",
          },
          {
            type: "DEFAULT",
            id: "5dadd13c-7723-4d26-ba81-d59b82db1b37",
            source_node_id: "035842e0-34ed-43af-97de-a706e40912ae",
            source_handle_id: "72157fce-fc16-44d8-a00d-506738a20730",
            target_node_id: "2c368766-015e-4d2f-8f57-01937038a4b2",
            target_handle_id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
          },
        ],
        nodes: [
          {
            id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
            type: "ENTRYPOINT",
            data: {
              label: "Entrypoint Node",
              source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
            },
            inputs: [],
            display_data: { position: { x: 0, y: -50 } },
            base: null,
            definition: null,
          },
          {
            id: "035842e0-34ed-43af-97de-a706e40912ae",
            label: "ToolCallingNode",
            type: "GENERIC",
            base: {
              name: "ToolCallingNode",
              module: [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "tool_calling_node",
                "node",
              ],
            },
            definition: {
              name: "ToolCallingNode",
              module: [
                "src",
                "testsubworkflowtoolcallingnode",
                "nodes",
                "tool_calling_node",
              ],
            },
            display_data: { position: { x: 200, y: -50 } },
            trigger: {
              id: "f9b4a4ce-68ae-45f4-9e29-38b588abdf97",
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            ports: [
              {
                id: "72157fce-fc16-44d8-a00d-506738a20730",
                name: "default",
                type: "DEFAULT",
              },
            ],
            adornments: null,
            attributes: [
              {
                id: "df3761db-067a-4fe9-9fc3-ba270786fcf6",
                name: "ml_model",
                value: {
                  type: "CONSTANT_VALUE",
                  value: { type: "STRING", value: "gpt-4o-mini" },
                },
              },
              {
                id: "0079b429-3b1c-4f7c-9ccf-185ace4dcbb2",
                name: "functions",
                value: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "JSON",
                    value: [
                      {
                        name: "FunctionTest",
                        type: "INLINE_WORKFLOW",
                        description: "a testing function",
                        exec_config: {
                          input_variables: [],
                          state_variables: [],
                          output_variables: [
                            {
                              id: "4ad75353-5845-4212-b4b1-db7193dacaac",
                              key: "final_output",
                              type: "STRING",
                            },
                          ],
                          workflow_raw_data: {
                            edges: [
                              {
                                id: "ee2bd7a2-c4db-4778-b1cf-b85de7e187a0",
                                type: "DEFAULT",
                                source_node_id:
                                  "32fbca40-5f46-4b55-96c3-f05b4a9071e5",
                                target_node_id:
                                  "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                source_handle_id:
                                  "911c0ca6-80c4-4475-b7dc-4c7400082cff",
                                target_handle_id:
                                  "a5298668-d808-4a45-a62e-790943948e8a",
                              },
                              {
                                id: "c7232331-a7dd-41a1-82de-e89af0edaabc",
                                type: "DEFAULT",
                                source_node_id:
                                  "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                target_node_id:
                                  "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                                source_handle_id:
                                  "9a9e4ef6-febf-4093-a515-217bbb1373db",
                                target_handle_id:
                                  "ff540c66-cd0d-41a7-a6a5-7ba45212f2d3",
                              },
                            ],
                            nodes: [
                              {
                                id: "32fbca40-5f46-4b55-96c3-f05b4a9071e5",
                                base: null,
                                data: {
                                  label: "Entrypoint Node",
                                  source_handle_id:
                                    "911c0ca6-80c4-4475-b7dc-4c7400082cff",
                                },
                                type: "ENTRYPOINT",
                                inputs: [],
                                definition: null,
                                display_data: { position: { x: 0, y: -50 } },
                              },
                              {
                                id: "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                base: {
                                  name: "BaseNode",
                                  module: [
                                    "vellum",
                                    "workflows",
                                    "nodes",
                                    "bases",
                                    "base",
                                  ],
                                },
                                type: "GENERIC",
                                label: "MyAdditionNode",
                                ports: [
                                  {
                                    id: "9a9e4ef6-febf-4093-a515-217bbb1373db",
                                    name: "default",
                                    type: "DEFAULT",
                                  },
                                ],
                                outputs: [
                                  {
                                    id: "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                                    name: "result",
                                    type: "NUMBER",
                                    value: null,
                                  },
                                ],
                                trigger: {
                                  id: "a5298668-d808-4a45-a62e-790943948e8a",
                                  merge_behavior: "AWAIT_ATTRIBUTES",
                                },
                                adornments: null,
                                attributes: [
                                  {
                                    id: "aed3bcbb-d243-4a77-bb5e-409e9a28e868",
                                    name: "arg1",
                                    value: {
                                      type: "CONSTANT_VALUE",
                                      value: { type: "JSON", value: null },
                                    },
                                  },
                                ],
                                definition: {
                                  name: "MyAdditionNode",
                                  module: [
                                    "src",
                                    "testsubworkflowtoolcallingnode",
                                    "nodes",
                                    "tool_calling_node",
                                    "function_test",
                                    "nodes",
                                    "my_addition",
                                  ],
                                },
                                display_data: { position: { x: 200, y: -50 } },
                              },
                              {
                                id: "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                                base: {
                                  name: "FinalOutputNode",
                                  module: [
                                    "vellum",
                                    "workflows",
                                    "nodes",
                                    "displayable",
                                    "final_output_node",
                                    "node",
                                  ],
                                },
                                data: {
                                  name: "final_output",
                                  label: "Final Output1",
                                  output_id:
                                    "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                                  output_type: "STRING",
                                  node_input_id:
                                    "5f0e8e8b-5382-4b40-9bf7-a75846cfa4a4",
                                  target_handle_id:
                                    "ff540c66-cd0d-41a7-a6a5-7ba45212f2d3",
                                },
                                type: "TERMINAL",
                                inputs: [
                                  {
                                    id: "5f0e8e8b-5382-4b40-9bf7-a75846cfa4a4",
                                    key: "node_input",
                                    value: {
                                      rules: [
                                        {
                                          data: {
                                            node_id:
                                              "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                            output_id:
                                              "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                                          },
                                          type: "NODE_OUTPUT",
                                        },
                                      ],
                                      combinator: "OR",
                                    },
                                  },
                                ],
                                outputs: [
                                  {
                                    id: "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                                    name: "value",
                                    type: "STRING",
                                    value: {
                                      type: "NODE_OUTPUT",
                                      node_id:
                                        "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                      node_output_id:
                                        "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                                    },
                                  },
                                ],
                                definition: {
                                  name: "FinalOutput1",
                                  module: [
                                    "src",
                                    "testsubworkflowtoolcallingnode",
                                    "nodes",
                                    "tool_calling_node",
                                    "function_test",
                                    "nodes",
                                    "final_output",
                                  ],
                                },
                                display_data: { position: { x: 400, y: -50 } },
                              },
                            ],
                            definition: {
                              name: "FunctionTest",
                              module: [
                                "src",
                                "testsubworkflowtoolcallingnode",
                                "nodes",
                                "tool_calling_node",
                                "function_test",
                                "workflow",
                              ],
                            },
                            display_data: { viewport: { x: 0, y: 0, zoom: 1 } },
                            output_values: [
                              {
                                value: {
                                  type: "NODE_OUTPUT",
                                  node_id:
                                    "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                                  node_output_id:
                                    "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                                },
                                output_variable_id:
                                  "4ad75353-5845-4212-b4b1-db7193dacaac",
                              },
                            ],
                          },
                        },
                      },
                    ],
                  },
                },
              },
            ],
            outputs: [
              {
                id: "c18a8725-21e1-4736-a77c-76d0fc035176",
                name: "text",
                type: "STRING",
                value: null,
              },
              {
                id: "5a9ad073-c670-43d2-9198-a08e9fdda7ad",
                name: "chat_history",
                type: "CHAT_HISTORY",
                value: null,
              },
            ],
          },
          {
            id: "2c368766-015e-4d2f-8f57-01937038a4b2",
            type: "TERMINAL",
            data: {
              label: "Final Output",
              name: "final_output",
              target_handle_id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
              output_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
              output_type: "STRING",
              node_input_id: "287431be-000d-498d-9dd0-b8dddbce5a5a",
            },
            inputs: [
              {
                id: "287431be-000d-498d-9dd0-b8dddbce5a5a",
                key: "node_input",
                value: {
                  rules: [
                    {
                      type: "NODE_OUTPUT",
                      data: {
                        node_id: "035842e0-34ed-43af-97de-a706e40912ae",
                        output_id: "c18a8725-21e1-4736-a77c-76d0fc035176",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
            ],
            display_data: { position: { x: 400, y: -50 } },
            base: null,
            definition: {
              name: "FinalOutput",
              module: [
                "src",
                "testsubworkflowtoolcallingnode",
                "nodes",
                "final_output",
              ],
            },
            trigger: {
              id: "af15d1e2-2ea2-485c-933a-142db6f9b2d4",
              merge_behavior: "AWAIT_ANY",
            },
            outputs: [
              {
                id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
                name: "value",
                type: "STRING",
                value: {
                  type: "NODE_OUTPUT",
                  node_id: "035842e0-34ed-43af-97de-a706e40912ae",
                  node_output_id: "c18a8725-21e1-4736-a77c-76d0fc035176",
                },
              },
            ],
          },
        ],
        definition: {
          name: "Workflow",
          module: ["src", "testsubworkflowtoolcallingnode", "workflow"],
        },
        display_data: {
          viewport: {
            x: 66.36363636363637,
            y: 235.89577992506412,
            zoom: 1.4395582725300728,
          },
        },
        output_values: [
          {
            output_variable_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
            value: {
              type: "NODE_OUTPUT",
              node_id: "2c368766-015e-4d2f-8f57-01937038a4b2",
              node_output_id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
            },
          },
        ],
      },
      input_variables: [],
      output_variables: [
        {
          id: "f04ec2cc-fd32-42b7-aac8-273bfaa3a283",
          key: "final_output",
          type: "STRING",
        },
      ],
      packages: [],
    };

    const project = new WorkflowProjectGenerator({
      absolutePathToOutputDirectory: tempDir,
      workflowVersionExecConfigData: displayData,
      moduleName: "src.testsubworkflowtoolcallingnode",
      vellumApiKey: "<TEST_API_KEY>",
    });

    await project.generateCode();

    expectProjectFileToMatchSnapshot([
      "src",
      "testsubworkflowtoolcallingnode",
      "nodes",
      "tool_calling_node",
      "function_test",
      "__init__.py",
    ]);
  });

  describe("module data with additional files", () => {
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
      module_data: {
        additional_files: {
          "utils.py": "def helper_function():\n    return 'Hello from utils'\n",
          "config/settings.json": '{"debug": true, "version": "1.0.0"}',
          "nested/deep/file.txt": "This is a nested file content",
        },
      },
    };

    it("should write additional files from module_data to disk during code generation", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);

      expectProjectFileToExist(["code", "utils.py"]);
      expectProjectFileToExist(["code", "config", "settings.json"]);
      expectProjectFileToExist(["code", "nested", "deep", "file.txt"]);

      const utilsPath = join(tempDir, "code", "utils.py");
      const configPath = join(tempDir, "code", "config", "settings.json");
      const nestedPath = join(tempDir, "code", "nested", "deep", "file.txt");

      expect(fs.readFileSync(utilsPath, "utf-8")).toBe(
        "def helper_function():\n    return 'Hello from utils'\n"
      );
      expect(fs.readFileSync(configPath, "utf-8")).toBe(
        '{"debug": true, "version": "1.0.0"}'
      );
      expect(fs.readFileSync(nestedPath, "utf-8")).toBe(
        "This is a nested file content"
      );
    });

    it("should handle empty additional files gracefully", async () => {
      const displayDataWithEmptyFiles = {
        ...displayData,
        module_data: {
          additional_files: {},
        },
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayDataWithEmptyFiles,
        moduleName: "code",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      expectProjectFileToExist(["code", "workflow.py"]);
    });
  });

  describe("Get inline prompt node files", () => {
    const functionsAttribute: NodeAttributeType = {
      id: uuidv4(),
      name: "functions",
      value: {
        type: "CONSTANT_VALUE",
        value: {
          type: "JSON",
          value: [
            {
              type: "CODE_EXECUTION",
              name: "my_test_function",
              description: "Some sample test function",
              src: 'def my_test_function(arg1: str, arg2: str) -> str:\n    """Processes input data and returns formatted output"""\n    return f"arg1: {arg1}, arg2: {arg2}"',
              definition: {
                name: "my_test_function",
                description: "Some sample test function",
                parameters: {
                  type: "object",
                  required: ["arg1", "arg2"],
                  properties: {
                    arg1: { type: "string" },
                    arg2: { type: "string" },
                  },
                },
                state: null,
                cache_config: null,
                forced: null,
                strict: null,
              },
            },
          ],
        },
      },
    };

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
            id: "inline-prompt-node",
            type: WorkflowNodeType.PROMPT,
            attributes: [functionsAttribute],
            inputs: [],
            data: {
              variant: "INLINE",
              label: "Inline Prompt Node",
              ml_model_name: "gpt-4",
              output_id: "output-id",
              array_output_id: "array-output-id",
              source_handle_id: "source-handle-id",
              target_handle_id: "target-handle-id",
              exec_config: {
                prompt_template_block_data: {
                  version: 1.0,
                  blocks: [
                    {
                      id: "block-1",
                      block_type: "JINJA",
                      state: "ENABLED",
                      properties: {
                        template: "Hello world",
                      },
                    },
                  ],
                },
                input_variables: [],
                parameters: {
                  temperature: 0.7,
                },
              },
            },
            trigger: {
              id: "inline-prompt-trigger",
              merge_behavior: "AWAIT_ATTRIBUTES",
            },
            ports: [
              {
                id: "inline-prompt-default-port",
                name: "default",
                type: "DEFAULT",
              },
            ],
            base: {
              name: "InlinePromptNode",
              module: [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "inline_prompt_node",
              ],
            },
            outputs: [],
          },
        ],
        edges: [
          {
            source_node_id: "entry",
            source_handle_id: "entry_source",
            target_node_id: "inline-prompt-node",
            target_handle_id: "inline-prompt-trigger",
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
    it("should get files", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "inline_prompt_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
      });

      await project.generateCode();
      const pythonCodeMergeableNodeFiles =
        project.getPythonCodeMergeableNodeFiles();
      expect(pythonCodeMergeableNodeFiles).toEqual(
        new Set(["nodes/inline_prompt_node.py"])
      );
    });

    it("should generate the function at top level of node file", async () => {
      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "inline_prompt_test",
        vellumApiKey: "<TEST_API_KEY>",
        workflowVersionExecConfigData: displayData,
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot([
        "inline_prompt_test",
        "nodes",
        "inline_prompt_node.py",
      ]);
    });
  });

  describe("getPythonCodeMergeableNodeFiles", () => {
    it("should collect mergeable files from both top-level and nested workflow contexts", async () => {
      const workflowData = {
        workflow_raw_data: {
          nodes: [
            {
              id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint Node",
                source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
              },
              inputs: [],
              display_data: {
                position: { x: 0, y: -50 },
              },
              base: null,
              definition: null,
            },
            {
              id: "32ccbdca-e986-44ff-bd26-78c2c8cb4d67",
              type: "SUBWORKFLOW",
              data: {
                // Add the missing required fields
                label: "Subworkflow",
                source_handle_id: "d1c3d678-fb6a-417f-b46c-b1b7e0d302c8",
                target_handle_id: "fbf37365-445c-4f4b-9d47-c1e08191f4dd",
                error_output_id: null,
                variant: "INLINE",
                workflow_raw_data: {
                  nodes: [
                    {
                      id: "4a9a3524-44a3-453f-925f-679db1bd0e59",
                      type: "ENTRYPOINT",
                      data: {
                        label: "Entrypoint Node",
                        source_handle_id:
                          "90c9baa6-198c-418e-9425-8dc0fc98d0c3",
                      },
                      inputs: [],
                      display_data: {
                        position: { x: 0, y: -50 },
                      },
                      base: null,
                      definition: null,
                    },
                    {
                      id: "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                      label: "MyAdditionNode",
                      type: "GENERIC",
                      base: {
                        name: "BaseNode",
                        module: [
                          "vellum",
                          "workflows",
                          "nodes",
                          "bases",
                          "base",
                        ],
                      },
                      definition: {
                        name: "MyAdditionNode",
                        module: [
                          "testpushstate",
                          "nodes",
                          "subworkflow",
                          "nodes",
                          "my_addition",
                        ],
                      },
                      display_data: {
                        position: { x: 200, y: -50 },
                      },
                      trigger: {
                        id: "a5298668-d808-4a45-a62e-790943948e8a",
                        merge_behavior: "AWAIT_ATTRIBUTES",
                      },
                      ports: [
                        {
                          id: "9a9e4ef6-febf-4093-a515-217bbb1373db",
                          name: "default",
                          type: "DEFAULT",
                        },
                      ],
                      attributes: [],
                      outputs: [
                        {
                          id: "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                          name: "result",
                          type: "NUMBER",
                          value: null,
                        },
                      ],
                    },
                    {
                      id: "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                      type: "TERMINAL",
                      data: {
                        label: "Final Output1",
                        name: "final_output",
                        target_handle_id:
                          "ff540c66-cd0d-41a7-a6a5-7ba45212f2d3",
                        output_id: "b649f934-f4d9-499d-a6e5-06cb0da61ba8",
                        output_type: "NUMBER",
                        node_input_id: "5f0e8e8b-5382-4b40-9bf7-a75846cfa4a4",
                      },
                      inputs: [
                        {
                          id: "5f0e8e8b-5382-4b40-9bf7-a75846cfa4a4",
                          key: "node_input",
                          value: {
                            rules: [
                              {
                                type: "NODE_OUTPUT",
                                data: {
                                  node_id:
                                    "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                                  output_id:
                                    "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                                },
                              },
                            ],
                            combinator: "OR",
                          },
                        },
                      ],
                      display_data: {
                        position: { x: 400, y: -50 },
                      },
                      base: {
                        name: "FinalOutputNode",
                        module: [
                          "vellum",
                          "workflows",
                          "nodes",
                          "displayable",
                          "final_output_node",
                          "node",
                        ],
                      },
                      definition: {
                        name: "FinalOutput1",
                        module: [
                          "testpushstate",
                          "nodes",
                          "subworkflow",
                          "nodes",
                          "final_output",
                        ],
                      },
                      trigger: {
                        id: "ff540c66-cd0d-41a7-a6a5-7ba45212f2d3",
                        merge_behavior: "AWAIT_ANY",
                      },
                      outputs: [
                        {
                          id: "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                          name: "value",
                          type: "NUMBER",
                          value: {
                            type: "NODE_OUTPUT",
                            node_id: "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                            node_output_id:
                              "3d8e40cb-2aa8-44bd-ae6a-708a9fbc4779",
                          },
                        },
                      ],
                    },
                  ],
                  edges: [
                    {
                      type: "DEFAULT",
                      id: "369ae0d2-337a-4860-81e7-9a4b8ccbde5d",
                      source_node_id: "4a9a3524-44a3-453f-925f-679db1bd0e59",
                      source_handle_id: "90c9baa6-198c-418e-9425-8dc0fc98d0c3",
                      target_node_id: "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                      target_handle_id: "a5298668-d808-4a45-a62e-790943948e8a",
                    },
                    {
                      type: "DEFAULT",
                      id: "95cce8f0-7956-4e14-8bcf-d23152fee535",
                      source_node_id: "195cd69d-3d2d-41e4-a432-16c433cb8d34",
                      source_handle_id: "9a9e4ef6-febf-4093-a515-217bbb1373db",
                      target_node_id: "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                      target_handle_id: "ff540c66-cd0d-41a7-a6a5-7ba45212f2d3",
                    },
                  ],
                  display_data: {
                    viewport: { x: 0, y: 0, zoom: 1 },
                  },
                  definition: {
                    name: "SubworkflowWorkflow",
                    module: [
                      "testpushstate",
                      "nodes",
                      "subworkflow",
                      "workflow",
                    ],
                  },
                  output_values: [
                    {
                      output_variable_id:
                        "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                      value: {
                        type: "NODE_OUTPUT",
                        node_id: "eb4f0a74-c3d0-4c08-b91a-70e43e667fe9",
                        node_output_id: "d4ccb8a1-3a3a-4796-b819-659cb7840208",
                      },
                    },
                  ],
                },
                input_variables: [],
                output_variables: [
                  {
                    id: "b649f934-f4d9-499d-a6e5-06cb0da61ba8",
                    key: "final_output",
                    type: "NUMBER",
                  },
                ],
                state_variables: [],
              },
              inputs: [],
              display_data: {
                position: { x: 200, y: -50 },
              },
              base: {
                name: "InlineSubworkflowNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "inline_subworkflow_node",
                  "node",
                ],
              },
              definition: {
                name: "Subworkflow",
                module: ["testpushstate", "nodes", "subworkflow"],
              },
              trigger: {
                id: "fbf37365-445c-4f4b-9d47-c1e08191f4dd",
                merge_behavior: "AWAIT_ANY",
              },
              ports: [
                {
                  id: "d1c3d678-fb6a-417f-b46c-b1b7e0d302c8",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              outputs: [
                {
                  id: "b649f934-f4d9-499d-a6e5-06cb0da61ba8",
                  name: "final_output",
                  type: "NUMBER",
                  value: null,
                },
              ],
            },
            {
              id: "8c8c3033-a987-47a7-9cc9-f227942a2af2",
              label: "YetAnotherAdditionNode",
              type: "GENERIC",
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              definition: {
                name: "YetAnotherAdditionNode",
                module: ["testpushstate", "nodes", "yet_another_addition"],
              },
              display_data: {
                position: { x: 400, y: -50 },
              },
              trigger: {
                id: "d51893b0-7cf0-4fb9-9f1a-a29a64a80852",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: "3bb19610-4525-430c-b329-4c34c79051f8",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              attributes: [
                {
                  id: "fde89884-72e1-46a4-b9db-72c371c512d6",
                  name: "arg1",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "32ccbdca-e986-44ff-bd26-78c2c8cb4d67",
                    node_output_id: "b649f934-f4d9-499d-a6e5-06cb0da61ba8",
                  },
                },
              ],
              outputs: [
                {
                  id: "d8e99c76-c24a-4ce0-bb66-e3b8ff0caa1f",
                  name: "result",
                  type: "NUMBER",
                  value: null,
                },
              ],
            },
            {
              id: "beb687d9-71bd-4dcf-aef7-af7ecf4aa536",
              type: "TERMINAL",
              data: {
                label: "Final Output",
                name: "final_output",
                target_handle_id: "f1213459-4514-474d-b540-cbc399e88468",
                output_id: "16b9fa94-c99b-4290-a57c-2acb5283051f",
                output_type: "NUMBER",
                node_input_id: "b2c4af5d-207d-43ba-ad72-8bc2e0b65913",
              },
              inputs: [
                {
                  id: "b2c4af5d-207d-43ba-ad72-8bc2e0b65913",
                  key: "node_input",
                  value: {
                    rules: [
                      {
                        type: "NODE_OUTPUT",
                        data: {
                          node_id: "8c8c3033-a987-47a7-9cc9-f227942a2af2",
                          output_id: "d8e99c76-c24a-4ce0-bb66-e3b8ff0caa1f",
                        },
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              display_data: {
                position: { x: 600, y: -50 },
              },
              base: {
                name: "FinalOutputNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "displayable",
                  "final_output_node",
                  "node",
                ],
              },
              definition: null,
              trigger: {
                id: "f1213459-4514-474d-b540-cbc399e88468",
                merge_behavior: "AWAIT_ANY",
              },
              outputs: [
                {
                  id: "16b9fa94-c99b-4290-a57c-2acb5283051f",
                  name: "value",
                  type: "NUMBER",
                  value: {
                    type: "NODE_OUTPUT",
                    node_id: "8c8c3033-a987-47a7-9cc9-f227942a2af2",
                    node_output_id: "d8e99c76-c24a-4ce0-bb66-e3b8ff0caa1f",
                  },
                },
              ],
            },
          ],
          edges: [
            {
              type: "DEFAULT",
              id: "62800510-e61d-4104-954a-9c7a6e8476d0",
              source_node_id: "63884a7b-c01c-4cbc-b8d4-abe0a8796f6b",
              source_handle_id: "eba8fd73-57ab-4d7b-8f75-b54dbe5fc8ba",
              target_node_id: "32ccbdca-e986-44ff-bd26-78c2c8cb4d67",
              target_handle_id: "fbf37365-445c-4f4b-9d47-c1e08191f4dd",
            },
            {
              type: "DEFAULT",
              id: "26b5af3b-3d3b-47c0-8ed8-10fdd3844422",
              source_node_id: "32ccbdca-e986-44ff-bd26-78c2c8cb4d67",
              source_handle_id: "d1c3d678-fb6a-417f-b46c-b1b7e0d302c8",
              target_node_id: "8c8c3033-a987-47a7-9cc9-f227942a2af2",
              target_handle_id: "d51893b0-7cf0-4fb9-9f1a-a29a64a80852",
            },
            {
              type: "DEFAULT",
              id: "c6aae411-e38c-44a0-828b-66210eaff6ef",
              source_node_id: "8c8c3033-a987-47a7-9cc9-f227942a2af2",
              source_handle_id: "3bb19610-4525-430c-b329-4c34c79051f8",
              target_node_id: "beb687d9-71bd-4dcf-aef7-af7ecf4aa536",
              target_handle_id: "f1213459-4514-474d-b540-cbc399e88468",
            },
          ],
          display_data: {
            viewport: { x: 0, y: 0, zoom: 1 },
          },
          definition: {
            name: "Workflow",
            module: ["testpushstate", "workflow"],
          },
          output_values: [
            {
              output_variable_id: "16b9fa94-c99b-4290-a57c-2acb5283051f",
              value: {
                type: "NODE_OUTPUT",
                node_id: "beb687d9-71bd-4dcf-aef7-af7ecf4aa536",
                node_output_id: "16b9fa94-c99b-4290-a57c-2acb5283051f",
              },
            },
          ],
        },
        input_variables: [
          {
            id: "bbd9e32f-7496-449e-9654-645e4024ad81",
            key: "text",
            type: "STRING",
            required: true,
          },
        ],
        output_variables: [
          {
            id: "16b9fa94-c99b-4290-a57c-2acb5283051f",
            key: "final_output",
            type: "NUMBER",
          },
        ],
        state_variables: [
          {
            id: "c38b8c20-22b5-4af8-8e13-36f1250bab35",
            key: "total",
            type: "NUMBER",
            required: false,
          },
        ],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: workflowData,
        moduleName: "testing",
        vellumApiKey: "<TEST_API_KEY>",
      });

      await project.generateCode();

      expect(project.workflowContext.getErrors()).toHaveLength(0);

      const mergeableFiles = project.getPythonCodeMergeableNodeFiles();

      expect(mergeableFiles.size).toBe(2);

      expect(mergeableFiles).toContain("nodes/yet_another_addition.py"); // Top-level generic node
      expect(mergeableFiles).toContain(
        "nodes/subworkflow/nodes/my_addition.py"
      ); // Nested generic node in subworkflow
    });
    it("should get node with should_file_merge field", async () => {
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
                  "displayable",
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
              should_file_merge: true,
              outputs: [],
              trigger: {
                id: "d8d60185-e88a-467b-84f4-e5fddd8b3209",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              adornments: null,
              attributes: [],
              definition: {
                name: "GetCurrentWeatherNode",
                module: ["testing", "nodes", "tool_calling_node"],
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
        moduleName: "testing",
        vellumApiKey: "<TEST_API_KEY>",
      });
      await project.generateCode();

      const mergeableFiles = project.getPythonCodeMergeableNodeFiles();

      expect(mergeableFiles.size).toBe(1);
      expect(mergeableFiles).toContain("nodes/tool_calling_node.py");
    });
  });

  describe("subworkflow with inner and outer generic nodes", () => {
    it("should generate workflow with subworkflow node containing inner generic node and outer generic node", async () => {
      /**
       * Tests that a workflow with a subworkflow node containing an inner generic node
       * and an outer generic node with edge from inner to outer generates correctly.
       */

      // GIVEN a workflow with subworkflow node containing inner generic node and outer generic node
      const displayData = {
        workflow_raw_data: {
          nodes: [
            {
              id: "entrypoint-node",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint Node",
                source_handle_id: "entrypoint-source-handle",
              },
              inputs: [],
              display_data: {
                position: { x: 0, y: -50 },
              },
              base: null,
              definition: null,
            },
            {
              id: "subworkflow-node",
              type: "SUBWORKFLOW",
              data: {
                label: "Subworkflow Node",
                source_handle_id: "subworkflow-source-handle",
                target_handle_id: "subworkflow-target-handle",
                error_output_id: null,
                variant: "INLINE",
                workflow_raw_data: {
                  nodes: [
                    {
                      id: "inner-entrypoint-node",
                      type: "ENTRYPOINT",
                      data: {
                        label: "Entrypoint Node",
                        source_handle_id: "inner-entrypoint-source-handle",
                      },
                      inputs: [],
                      display_data: {
                        position: { x: 0, y: -50 },
                      },
                      base: null,
                      definition: null,
                    },
                    {
                      id: "inner-generic-node",
                      label: "Inner",
                      type: "GENERIC",
                      base: {
                        name: "BaseNode",
                        module: [
                          "vellum",
                          "workflows",
                          "nodes",
                          "bases",
                          "base",
                        ],
                      },
                      definition: {
                        name: "Inner",
                        module: [
                          "subworkflow_test",
                          "nodes",
                          "subworkflow_node",
                          "nodes",
                          "inner",
                        ],
                      },
                      display_data: {
                        position: { x: 200, y: -50 },
                      },
                      trigger: {
                        id: "inner-generic-trigger",
                        merge_behavior: "AWAIT_ATTRIBUTES",
                      },
                      ports: [
                        {
                          id: "inner-generic-port",
                          name: "default",
                          type: "DEFAULT",
                        },
                      ],
                      attributes: [],
                      outputs: [
                        {
                          id: "inner-generic-output",
                          name: "result",
                          type: "STRING",
                          value: null,
                        },
                      ],
                    },
                    {
                      id: "inner-terminal-node",
                      type: "TERMINAL",
                      data: {
                        label: "Inner Terminal",
                        name: "inner_result",
                        target_handle_id: "inner-terminal-trigger",
                        output_id: "inner-terminal-output",
                        output_type: "STRING",
                        node_input_id: "inner-terminal-input",
                      },
                      inputs: [
                        {
                          id: "inner-terminal-input",
                          key: "inner_result",
                          value: {
                            combinator: "OR",
                            rules: [
                              {
                                type: "NODE_OUTPUT",
                                data: {
                                  node_id: "inner-generic-node",
                                  output_id: "inner-generic-output",
                                },
                              },
                            ],
                          },
                        },
                      ],
                      display_data: {
                        position: { x: 400, y: -50 },
                      },
                      base: null,
                      definition: null,
                      trigger: {
                        id: "inner-terminal-trigger",
                        merge_behavior: "AWAIT_ATTRIBUTES",
                      },
                      ports: [],
                      attributes: [],
                      outputs: [
                        {
                          id: "inner-terminal-output",
                          name: "inner_result",
                          type: "STRING",
                          value: null,
                        },
                      ],
                    },
                  ],
                  edges: [
                    {
                      id: "inner-edge",
                      source_node_id: "inner-entrypoint-node",
                      source_handle_id: "inner-entrypoint-source-handle",
                      target_node_id: "inner-generic-node",
                      target_handle_id: "inner-generic-trigger",
                      type: "DEFAULT",
                    },
                    {
                      id: "inner-to-terminal-edge",
                      source_node_id: "inner-generic-node",
                      source_handle_id: "inner-generic-port",
                      target_node_id: "inner-terminal-node",
                      target_handle_id: "inner-terminal-trigger",
                      type: "DEFAULT",
                    },
                    {
                      id: "edge-3",
                      source_node_id: "inner-generic-node",
                      source_handle_id: "inner-generic-port",
                      target_node_id: "outer-generic-node",
                      target_handle_id: "outer-generic-trigger",
                      type: "DEFAULT",
                    },
                  ],
                },
                input_variables: [],
                output_variables: [
                  {
                    id: "subworkflow-output-var",
                    key: "final-output",
                    type: "STRING",
                  },
                ],
              },
              inputs: [],
              display_data: {
                position: { x: 200, y: -50 },
              },
              base: {
                name: "InlineSubworkflowNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "inline_subworkflow_node",
                  "node",
                ],
              },
              definition: null,
            },
            {
              id: "outer-generic-node",
              label: "Outer",
              type: "GENERIC",
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              definition: {
                name: "Outer",
                module: ["subworkflow_test", "nodes", "outer"],
              },
              display_data: {
                position: { x: 400, y: -50 },
              },
              trigger: {
                id: "outer-generic-trigger",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
              ports: [
                {
                  id: "outer-generic-port",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              attributes: [],
              outputs: [
                {
                  id: "outer-generic-output",
                  name: "result",
                  type: "STRING",
                  value: null,
                },
              ],
            },
          ],
          edges: [
            {
              id: "edge-1",
              source_node_id: "entrypoint-node",
              source_handle_id: "entrypoint-source-handle",
              target_node_id: "subworkflow-node",
              target_handle_id: "subworkflow-target-handle",
              type: "DEFAULT",
            },
            {
              id: "edge-2",
              source_node_id: "subworkflow-node",
              source_handle_id: "subworkflow-source-handle",
              target_node_id: "outer-generic-node",
              target_handle_id: "outer-generic-trigger",
              type: "DEFAULT",
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
        vellumApiKey: "test-key",
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "subworkflow_node",
        "workflow.py",
      ]);

      // AND the outer generic node should be generated
      expectProjectFileToMatchSnapshot(["code", "nodes", "outer.py"]);

      // AND there should be no errors
      expect(project.workflowContext.getErrors()).toHaveLength(0);
    });
  });

  describe("LEGACY prompt node codegen", () => {
    it("should properly handle legacy prompt node even if ml model name is not found", async () => {
      const displayData = {
        workflow_raw_data: {
          nodes: [
            {
              id: "entrypoint-node",
              type: "ENTRYPOINT",
              inputs: [],
              data: {
                label: "Entrypoint Node",
                source_handle_id: "source-handle",
                target_handle_id: "entry-target",
              },
              display_data: {
                position: { x: 100, y: 100 },
                comment: null,
                width: null,
                height: null,
              },
              base: null,
              definition: null,
              trigger: {
                id: "entry-target",
                merge_behavior: "AWAIT_ANY",
              },
              ports: [
                {
                  id: "source-handle",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              adornments: null,
              outputs: [],
            },
            {
              id: "legacy-prompt-node",
              type: "PROMPT",
              data: {
                variant: "LEGACY",
                label: "Legacy Prompt Node",
                output_id: "output-1",
                array_output_id: "array-output-1",
                error_output_id: null,
                source_handle_id: "prompt-source",
                target_handle_id: "prompt-target",
                sandbox_routing_config: {
                  version: 2,
                  prompt_version_data: {
                    ml_model_to_workspace_id:
                      "b73088ce-1c42-48e8-ab8f-1931101c7721",
                    exec_config: {
                      parameters: {
                        stop: null,
                        temperature: 0.0,
                        max_tokens: 256,
                        top_p: 1.0,
                        top_k: 0,
                        frequency_penalty: 0.0,
                        presence_penalty: 0.0,
                        logit_bias: null,
                        custom_parameters: null,
                      },
                      input_variables: [
                        {
                          id: "input-var-1",
                          key: "query_str",
                          type: "STRING",
                          required: null,
                          default: null,
                          extensions: null,
                        },
                      ],
                      prompt_template_block_data: {
                        blocks: [
                          {
                            block_type: "CHAT_MESSAGE",
                            properties: {
                              blocks: [
                                {
                                  block_type: "JINJA",
                                  properties: {
                                    template: "You are a helpful assistant.",
                                    template_type: null,
                                  },
                                  id: "jinja-block-1",
                                  state: "ENABLED",
                                  cache_config: null,
                                },
                              ],
                              chat_role: "SYSTEM",
                              chat_source: null,
                              chat_message_unterminated: false,
                            },
                            id: "chat-block-1",
                            state: "ENABLED",
                            cache_config: null,
                          },
                        ],
                        version: 1,
                      },
                      settings: null,
                    },
                  },
                },
              },
              inputs: [
                {
                  id: "input-var-1",
                  key: "query_str",
                  value: {
                    rules: [
                      {
                        type: "INPUT_VARIABLE",
                        data: {
                          input_variable_id: "workflow-input-1",
                        },
                      },
                    ],
                    combinator: "OR",
                  },
                },
              ],
              display_data: {
                position: { x: 300, y: 100 },
                comment: null,
                width: null,
                height: null,
              },
              base: null,
              definition: null,
              trigger: {
                id: "prompt-target",
                merge_behavior: "AWAIT_ANY",
              },
              ports: [
                {
                  id: "prompt-source",
                  name: "default",
                  type: "DEFAULT",
                },
              ],
              adornments: null,
              outputs: [
                {
                  id: "output-1",
                  name: "result",
                  type: "STRING",
                },
              ],
            },
          ],
          edges: [
            {
              id: "edge-1",
              source_node_id: "entrypoint-node",
              source_handle_id: "source-handle",
              target_node_id: "legacy-prompt-node",
              target_handle_id: "prompt-target",
              type: "DEFAULT",
            },
          ],
        },
        input_variables: [
          {
            id: "workflow-input-1",
            key: "query_str",
            type: "STRING",
          },
        ],
        state_variables: [],
        output_variables: [],
      };

      const project = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        moduleName: "code",
        vellumApiKey: "test-key",
      });

      vi.spyOn(MlModels.prototype, "retrieve").mockRejectedValue(
        new Error("ML model not found")
      );

      await project.generateCode();

      expectProjectFileToMatchSnapshot([
        "code",
        "nodes",
        "legacy_prompt_node.py",
      ]);

      const allErrors = project.workflowContext.getErrors();
      expect(allErrors).toHaveLength(1);
      expect(allErrors[0]?.message).toContain(
        "Failed to fetch ML model name for ID b73088ce-1c42-48e8-ab8f-1931101c7721: Error: ML model not found"
      );
    });
  });

  describe("Node comments serialization", () => {
    it("should serialize node comments with values as docstrings in SDK", async () => {
      /**
       * Tests that node comments with values appear as docstrings in generated node classes.
       * This verifies the fix for the bug reported in APO-1037.
       */

      // GIVEN a workflow with a node that has a comment with a value
      const displayData = {
        workflow_raw_data: {
          edges: [
            {
              source_node_id: "entrypoint-node-id",
              source_handle_id: "entrypoint-source-handle",
              target_node_id: "test-node-id",
              target_handle_id: "target-handle-id",
              type: "DEFAULT",
              id: "edge-1",
            },
          ],
          nodes: [
            {
              id: "entrypoint-node-id",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint",
                source_handle_id: "entrypoint-source-handle",
              },
              inputs: [],
            },
            {
              id: "test-node-id",
              type: "TEMPLATING",
              data: {
                label: "Test Node",
                source_handle_id: "source-handle-id",
                target_handle_id: "target-handle-id",
                template_node_input_id: "template-input-id",
                output_id: "output-id",
                output_type: "STRING",
              },
              inputs: [
                {
                  id: "template-input-id",
                  key: "template",
                  value: {
                    combinator: "OR",
                    rules: [
                      {
                        type: "CONSTANT_VALUE",
                        data: {
                          type: "STRING",
                          value: "Hello world",
                        },
                      },
                    ],
                  },
                },
              ],
              display_data: {
                position: { x: 100, y: 100 },
                width: 300,
                height: 200,
                comment: {
                  expanded: true,
                  value:
                    "This is a test comment that should appear as a docstring",
                },
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
        strict: true,
      });

      await project.generateCode();

      expectProjectFileToMatchSnapshot(["code", "nodes", "test_node.py"]);
    });
  });
});
