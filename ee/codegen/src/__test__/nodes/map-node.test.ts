import { mkdir, readFile, rm } from "fs/promises";
import { join } from "path";

import { afterEach, beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  inlinePromptNodeDataInlineVariantFactory,
  mapNodeDataFactory,
} from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { createNodeContext } from "src/context";
import { MapNodeContext } from "src/context/node-context/map-node";
import { MapNode } from "src/generators/nodes/map-node";

describe("MapNode", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = makeTempDir("map-node-test");
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
      const nodeData = mapNodeDataFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`map node file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`map node inputs file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "map_node", "inputs.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`map node display file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });

  describe("with additional output", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });
      const nodeData = mapNodeDataFactory({
        outputVariables: [
          {
            id: "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fb",
            key: "first-output",
            type: "STRING",
          },
          {
            id: "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fc",
            key: "second-output",
            type: "STRING",
          },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`map node file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });

    it(`map node display file`, async () => {
      expect(
        await readFile(
          join(tempDir, "code", "display", "nodes", "map_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });

  describe("with state", () => {
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });

      // Add state variable to the workflow context
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "state-var-id",
            key: "state",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const nodeData = mapNodeDataFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      await node.persist();
    });

    it(`map node file with state should include second generic type parameter`, async () => {
      const content = await readFile(
        join(tempDir, "code", "nodes", "map_node", "__init__.py"),
        "utf-8"
      );
      expect(content).toMatchSnapshot();
      // Verify it includes both generic types: State and Any
      expect(content).toContain("MapNode[State, Any]");
      expect(content).toContain("from typing import Any");
      expect(content).toContain("from ...state import State");
    });
  });

  describe("with node output items", () => {
    it(`should generate items referencing another node's output`, async () => {
      /**
       * Tests that MapNode can reference another node's output for its items attribute.
       * This demonstrates the foundation for accessor patterns like PromptNode.Outputs.json["foo"].
       */

      // GIVEN a workflow context
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });

      // AND a PromptNode with an output
      const promptNodeData = inlinePromptNodeDataInlineVariantFactory().build();
      const promptNodeId = promptNodeData.id;
      const promptNodeOutputId = promptNodeData.data.outputId;

      await createNodeContext({
        workflowContext,
        nodeData: promptNodeData,
      });

      // AND a MapNode with items referencing the PromptNode's output
      const nodeData = mapNodeDataFactory({
        items: {
          id: "f34872c2-5c0e-45a3-b204-3af22d1028d3",
          key: "items",
          value: {
            rules: [
              {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: promptNodeId,
                  outputId: promptNodeOutputId,
                },
              },
            ],
            combinator: "OR",
          },
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MapNodeContext;

      const node = new MapNode({
        workflowContext,
        nodeContext,
      });

      // WHEN we persist the node
      await node.persist();

      // THEN the generated code should reference the PromptNode's output
      const content = await readFile(
        join(tempDir, "code", "nodes", "map_node", "__init__.py"),
        "utf-8"
      );
      expect(content).toMatchSnapshot();
      expect(content).toContain("PromptNode.Outputs.text");
    });
  });
});
