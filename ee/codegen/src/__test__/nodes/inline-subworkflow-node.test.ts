import { mkdir, readFile, rm } from "fs/promises";
import { join } from "path";

import { v4 as uuidv4 } from "uuid";
import { afterEach, beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  inlineSubworkflowNodeDataFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { createNodeContext } from "src/context";
import { InlineSubworkflowNodeContext } from "src/context/node-context/inline-subworkflow-node";
import { InlineSubworkflowNode } from "src/generators/nodes/inline-subworkflow-node";
import { AdornmentNode } from "src/types/vellum";

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
      const nodeData = inlineSubworkflowNodeDataFactory().build();

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
        nodes: [templatingNodeFactory({ label: "My node" }).build()],
      }).build();

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
      const adornmentData: AdornmentNode[] = [
        {
          id: "ae49ef72-6ad7-441a-a20d-76c71ad851ef",
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
      ];
      const nodeData = inlineSubworkflowNodeDataFactory({
        label: "My node",
        nodes: [templatingNodeFactory({ label: "My node" }).build()],
      })
        .withAdornments(adornmentData)
        .build();

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

  describe("nested workflow class name collision", () => {
    /**
     * Tests that when an internal node has the same name as what the nested workflow
     * class would be named, the nested workflow class gets a unique name.
     * This is the APO-2207 scenario where:
     * - Outer inline subworkflow node labeled "My Node" → nested workflow class "MyNodeWorkflow"
     * - Internal node labeled "My Node Workflow" → would also be "MyNodeWorkflow"
     * The fix ensures the nested workflow class gets renamed to avoid collision.
     */
    beforeEach(async () => {
      const workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });

      // GIVEN an inline subworkflow node labeled "My Node"
      // AND an internal node labeled "My Node Workflow" (same as what the nested workflow class would be named)
      const nodeData = inlineSubworkflowNodeDataFactory({
        label: "My Node",
        nodes: [templatingNodeFactory({ label: "My Node Workflow" }).build()],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as InlineSubworkflowNodeContext;

      const node = new InlineSubworkflowNode({
        workflowContext,
        nodeContext,
      });

      // WHEN we generate the code
      await node.persist();
    });

    it(`should generate unique nested workflow class name when internal node has same name`, async () => {
      // THEN the outer node file should reference a unique workflow class name
      const outerNodeContent = await readFile(
        join(tempDir, "code", "nodes", "my_node", "__init__.py"),
        "utf-8"
      );
      expect(outerNodeContent).toMatchSnapshot();

      // AND the nested workflow file should have the unique class name
      const workflowContent = await readFile(
        join(tempDir, "code", "nodes", "my_node", "workflow.py"),
        "utf-8"
      );
      expect(workflowContent).toMatchSnapshot();

      // AND the internal node should keep its original class name
      const internalNodeContent = await readFile(
        join(
          tempDir,
          "code",
          "nodes",
          "my_node",
          "nodes",
          "my_node_workflow.py"
        ),
        "utf-8"
      );
      expect(internalNodeContent).toMatchSnapshot();
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

      const nodeData = inlineSubworkflowNodeDataFactory().build();

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

    it(`inline subworkflow node file with state should include all three generic type parameters`, async () => {
      const content = await readFile(
        join(
          tempDir,
          "code",
          "nodes",
          "inline_subworkflow_node",
          "__init__.py"
        ),
        "utf-8"
      );
      expect(content).toMatchSnapshot();
      // Verify it includes all three generic types: StateType, InputsType, and InnerStateType
      expect(content).toContain("InlineSubworkflowNode[State");
      expect(content).toContain("from ...state import State");
      expect(content).toContain("from .workflow import");
    });
  });
});
