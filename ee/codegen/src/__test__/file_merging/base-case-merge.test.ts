import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { expect, vi } from "vitest";
import { v4 as uuidv4 } from "uuid";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { makeTempDir } from "../helpers/temp-dir";

import { WorkflowProjectGenerator } from "src/project";
import { WorkflowNodeType, type NodeAttribute } from "src/types/vellum";

/**
 * Emulates a simple Python file merging scenario at the TypeScript level by using
 * generateCode(originalArtifact) and asserting merged content is preserved.
 */
describe("TS-level Python file merging", () => {
  let tempDir: string;

  beforeEach(async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      {} as unknown as DocumentIndexRead
    );
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
    tempDir = makeTempDir("file-merging-test");
    await mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true });
  });

  it("should preserve content when originalArtifact equals previously generated content (base-case)", async () => {
    /**
     * Tests end-to-end merging using generateCode(originalArtifact).
     */

    // GIVEN a temp directory and inline display data that yields at least one mergeable node file
    const functionsAttribute: NodeAttribute = {
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
    } as const;

    const initialProject = new WorkflowProjectGenerator({
      absolutePathToOutputDirectory: tempDir,
      workflowVersionExecConfigData: displayData,
      moduleName: "code",
      vellumApiKey: "<TEST_API_KEY>",
      options: {
        codeExecutionNodeCodeRepresentationOverride: "STANDALONE",
      },
      strict: true,
    });
    // AND an initial project used to generate files for capturing the original artifact

    await initialProject.generateCode();

    const mergeable = initialProject.getPythonCodeMergeableNodeFiles();
    expect(
      mergeable.size,
      "Expected at least one mergeable node file to be present."
    ).toBeGreaterThan(0);

    const mergeablePath = Array.from(mergeable)[0] as string;
    const initialModuleDir = join(tempDir, ...initialProject.getModulePath());
    const originalContent = fs.readFileSync(
      join(initialModuleDir, mergeablePath),
      "utf-8"
    );
    const originalArtifact: Record<string, string> = {
      [mergeablePath]: originalContent,
    };
    // AND we capture the mergeable file contents as the original artifact

    // AND we reset the output directory to simulate a fresh generation
    await rm(tempDir, { recursive: true, force: true });
    await mkdir(tempDir, { recursive: true });

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

    // WHEN we generate code with originalArtifact to trigger Python file merging
    await project.generateCode(originalArtifact);

    const mergedModuleDir = join(tempDir, ...project.getModulePath());
    const mergedFilePath = join(mergedModuleDir, mergeablePath);
    // THEN the merged file exists
    expect(fs.existsSync(mergedFilePath)).toBe(true);

    const mergedContent = fs.readFileSync(mergedFilePath, "utf-8");
    expect(mergedContent.length).toBeGreaterThan(0);
    expect(mergedContent).toContain("def my_test_function(");
    expect(mergedContent).toContain('class InlinePromptNode(BaseInlinePromptNode):');
    expect(mergedContent).toContain('functions = [my_test_function]');
    expect(mergedContent).toMatch(/blocks\s*=\s*\[.*JinjaPromptBlock\(template="Hello world"\).*]/s);
  });
});
