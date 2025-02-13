import { mkdir, readFile, rm } from "fs/promises";
import { join } from "path";

import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inlineSubworkflowNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { createNodeContext } from "src/context";
import { InlineSubworkflowNodeContext } from "src/context/node-context/inline-subworkflow-node";
import { InlineSubworkflowNode } from "src/generators/nodes/inline-subworkflow-node";

describe("InlineSubworkflowNode", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = makeTempDir("inline-subworkflow-node-test");
    await mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true });
  });

  describe("basic", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = inlineSubworkflowNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as InlineSubworkflowNodeContext;

      const node = new InlineSubworkflowNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`inline subworkflow node file`, async () => {
      expect(
        await readFile(
          join(
            tempDir,
            "code",
            "nodes",
            "inline_subworkflow_node",
            "__init__.py"
          ),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`inline subworkflow node display file`, async () => {
      expect(
        await readFile(
          join(
            tempDir,
            "code",
            "display",
            "nodes",
            "inline_subworkflow_node",
            "__init__.py"
          ),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });
});
