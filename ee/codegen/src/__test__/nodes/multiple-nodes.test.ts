import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
  promptDeploymentNodeDataFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import {ConstantValuePointer} from "src/types/vellum";

describe("InlinePromptNode referenced by Conditional Node", () => {
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

describe("Prompt Deployment Node referenced by Conditional Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  const testCases = [
    {
      name: "takes output id",
      id: "fa015382-7e5b-404e-b073-1c5f01832169",
    },
    {
      name: "takes error output id",
      id: "72cb22fc-e2f5-4df3-9428-40436d58e57a",
    },
    {
      name: "takes array output id",
      id: "4d257095-e908-4fc3-8159-a6ac0018e1f1",
    },
  ];

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
  });

  it.each(testCases)("getNodeFile with $name", async ({ id }) => {
    await setupNode(id);
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it.each(testCases)("getNodeDisplayFile with $name", async ({ id }) => {
    await setupNode(id);
    node.getNodeDisplayFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it.each(testCases)("getNodeDefinition with $name", async ({ id }) => {
    await setupNode(id);
    expect(node.nodeContext.getNodeDefinition()).toMatchSnapshot();
  });

  async function setupNode(outputId: string) {
    const isErrorOutput = outputId === "72cb22fc-e2f5-4df3-9428-40436d58e57a";
    const promptDeploymentNode = promptDeploymentNodeDataFactory({
      errorOutputId: isErrorOutput ? outputId : undefined,
    });

    const promptDeploymentNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: promptDeploymentNode,
    })) as PromptDeploymentNodeContext;
    workflowContext.addNodeContext(promptDeploymentNodeContext);

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: outputId,
      inputReferenceNodeId: promptDeploymentNode.id,
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
  }
});

describe("InlinePromptNode referenced by Templating Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;
  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const promptNode = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
    });

    const promptNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;
    workflowContext.addNodeContext(promptNodeContext);

    const template: ConstantValuePointer = {
      type: "CONSTANT_VALUE",
      data: {
        type: "STRING",
        value: "{{ output[0].type }}",
      },
    };

    const templatingNode = templatingNodeFactory({
      inputReferenceId: promptNode.data.arrayOutputId,
      inputReferenceNodeId: promptNode.id,
      template: template,
    });

    const templatingNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: templatingNode,
    })) as TemplatingNodeContext;
    workflowContext.addNodeContext(templatingNodeContext);

    node = new TemplatingNode({
      workflowContext,
      nodeContext: templatingNodeContext,
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
