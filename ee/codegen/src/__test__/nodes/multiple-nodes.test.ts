import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";

describe("InlinePromptNode with Conditional Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;
  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "90c6afd3-06cc-430d-aed1-35937c062531",
          key: "text",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const errorOutputId = "72cb22fc-e2f5-4df3-9428-40436d58e57a";
    const promptNode = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
      errorOutputId: errorOutputId,
    });

    const promptNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;
    workflowContext.addNodeContext(promptNodeContext);

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: errorOutputId,
      inputReferenceNodeId: promptNode.id,
    });

    const conditionalNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: conditionalNode,
    })) as ConditionalNodeContext;
    workflowContext.addNodeContext(conditionalNodeContext);

    node = new ConditionalNode({
      workflowContext,
      nodeContext: conditionalNodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDisplayFile", async () => {
    node.getNodeDisplayFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDefinition", () => {
    expect(node.nodeContext.getNodeDefinition()).toMatchSnapshot();
  });
});
