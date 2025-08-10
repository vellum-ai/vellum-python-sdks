import { mkdir, rm } from "fs/promises";
import * as fs from "node:fs";
import { join } from "path";

import { v4 as uuidv4 } from "uuid";

import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { WorkflowProjectGenerator } from "src/project";

const rootDir = join(
  __dirname,
  "..",
  "..",
  "..",
  "python_file_merging/tests/fixtures/nodes"
);

const fixtureFilter = /base_case/;

const getFixturePaths = () => {
  const fixtureDirs = fs
    .readdirSync(rootDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => join(rootDir, d.name));

  return fixtureDirs
    .filter((d) => fixtureFilter.test(d))
    .map((d) => {
      const originalFilePath = join(d, "original.py");
      const generatedFilePath = join(d, "generic_node.json");
      const expectedFilePath = join(d, "expected.py");

      return {
        originalFilePath,
        generatedFilePath,
        expectedFilePath,
        label: d.split("/").pop() ?? "Unknown",
      };
    });
};

const nodeFileContents = getFixturePaths();

const singleGenericNodeWorkflowFactory = (
  genericNodeData: Record<string, string> = {}
) => {
  const entrypointNodeId = uuidv4();
  const entrypointSourceHandleId = uuidv4();
  const entrypointTargetHandleId = uuidv4();

  const genericNodeId = uuidv4();
  const genericSourceHandleId = uuidv4();
  const genericTriggerId = uuidv4();
  const genericDefaultPortId = uuidv4();

  const terminalNodeId = uuidv4();
  const terminalSourceHandleId = uuidv4();
  const terminalTargetHandleId = uuidv4();

  return {
    workflow_raw_data: {
      nodes: [
        {
          id: entrypointNodeId,
          type: "ENTRYPOINT",
          data: {
            label: "Entrypoint",
            source_handle_id: entrypointSourceHandleId,
            target_handle_id: entrypointTargetHandleId,
          },
          inputs: [],
        },
        {
          id: genericNodeId,
          type: "GENERIC",
          label: "My Custom Node",
          attributes: [],
          inputs: [],
          trigger: {
            id: genericTriggerId,
            merge_behavior: "AWAIT_ATTRIBUTES",
          },
          ports: [
            {
              id: genericDefaultPortId,
              name: "default",
              type: "DEFAULT",
            },
          ],
          base: {
            name: "BaseNode",
            module: ["vellum", "workflows", "nodes", "bases", "base"],
          },
          outputs: [],
          ...genericNodeData,
        },
        {
          id: terminalNodeId,
          type: "TERMINAL",
          data: {
            label: "Terminal",
            source_handle_id: terminalSourceHandleId,
            target_handle_id: terminalTargetHandleId,
            name: "output",
            output_id: uuidv4(),
            output_type: "STRING",
            node_input_id: uuidv4(),
          },
          inputs: [],
        },
      ],
      edges: [
        {
          source_node_id: entrypointNodeId,
          source_handle_id: "entry_source",
          target_node_id: genericNodeId,
          target_handle_id: genericTriggerId,
          type: "DEFAULT",
          id: uuidv4(),
        },
        {
          source_node_id: genericNodeId,
          source_handle_id: genericSourceHandleId,
          target_node_id: terminalNodeId,
          target_handle_id: terminalTargetHandleId,
          type: "DEFAULT",
          id: uuidv4(),
        },
      ],
    },
    input_variables: [],
    state_variables: [],
    output_variables: [],
    runner_config: {},
  };
};

/**
 * Emulates various Python file merging scenarios at the TypeScript level by using
 * generateCode(originalArtifact) and asserting merged content is preserved.
 */
describe("Python file merging", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = makeTempDir("file-merging-test");
    await mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true });
  });

  it.each(nodeFileContents)(
    "should preserve content when originalArtifact equals previously generated content ($label)",
    async ({ originalFilePath, generatedFilePath, expectedFilePath }) => {
      /**
       * Tests end-to-end merging using generateCode(originalArtifact).
       */

      // GIVEN a temp directory and inline display data that yields at least one mergeable node file
      const genericNodeData = fs.readFileSync(generatedFilePath, "utf-8");
      const displayData = singleGenericNodeWorkflowFactory(
        JSON.parse(genericNodeData)
      );

      const initialProject = new WorkflowProjectGenerator({
        absolutePathToOutputDirectory: tempDir,
        workflowVersionExecConfigData: displayData,
        vellumApiKey: "<TEST_API_KEY>",
        moduleName: "code",
      });

      // WHEN we generate code with the original artifact
      await initialProject.generateCode({
        "nodes/my_custom_node.py": fs.readFileSync(originalFilePath, "utf-8"),
      });

      // THEN the generated file should match the expected file
      const expectedContent = fs.readFileSync(expectedFilePath, "utf-8");

      const mergedFilePath = join(
        tempDir,
        ...initialProject.getModulePath(),
        "nodes",
        "my_custom_node.py"
      );
      const actualContent = fs.readFileSync(mergedFilePath, "utf-8");

      expect(actualContent).toBe(expectedContent);
    }
  );
});
