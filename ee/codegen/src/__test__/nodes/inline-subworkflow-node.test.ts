import { mkdir, readFile, rm } from "fs/promises";
import { join } from "path";

import { v4 as uuidv4 } from "uuid";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  inlineSubworkflowNodeDataFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
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

  describe("name collision", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = inlineSubworkflowNodeDataFactory({
        label: "My node",
        nodes: [templatingNodeFactory({ label: "My node" })],
      });

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

    it(`should handle subworkflow with same name as internal node`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "my_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();

      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "my_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();

      expect(
        await readFile(
          join(tempDir, "code", "nodes", "my_node", "nodes", "my_node.py"),
          "utf-8"
        )
      ).toMatchSnapshot();

      expect(
        await readFile(
          join(
            tempDir,
            "code",
            "display",
            "nodes",
            "my_node",
            "nodes",
            "my_node.py"
          ),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });
  describe("adornments", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = inlineSubworkflowNodeDataFactory({
        label: "My node",
        nodes: [templatingNodeFactory({ label: "My node" })],
        adornments: [
          {
            id: uuidv4(),
            label: "RetryNodeLabel",
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
            attributes: [
              {
                id: uuidv4(),
                name: "max_attempts",
                value: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "NUMBER",
                    value: 3,
                  },
                },
              },
              {
                id: uuidv4(),
                name: "delay",
                value: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "NUMBER",
                    value: 2,
                  },
                },
              },
            ],
          },
        ],
      });

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

    it(`should generate adornments`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "my_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "my_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });
});
