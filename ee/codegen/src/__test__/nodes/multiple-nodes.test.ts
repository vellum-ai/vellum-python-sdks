import { Writer } from "@fern-api/python-ast/core/Writer";
import { WorkflowDeploymentHistoryItem } from "vellum-ai/api";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
  promptDeploymentNodeDataFactory,
  subworkflowDeploymentNodeDataFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import { ConstantValuePointer } from "src/types/vellum";

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

    await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    });

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: errorOutputId,
      inputReferenceNodeId: promptNode.id,
    });

    const conditionalNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: conditionalNode,
    })) as ConditionalNodeContext;

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

  async function setupNode(outputId: string) {
    const isErrorOutput = outputId === "72cb22fc-e2f5-4df3-9428-40436d58e57a";
    const promptDeploymentNode = promptDeploymentNodeDataFactory({
      errorOutputId: isErrorOutput ? outputId : undefined,
    });

    await createNodeContext({
      workflowContext,
      nodeData: promptDeploymentNode,
    });

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: outputId,
      inputReferenceNodeId: promptDeploymentNode.id,
    });

    const conditionalNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: conditionalNode,
    })) as ConditionalNodeContext;

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

    (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;

    const template: ConstantValuePointer = {
      type: "CONSTANT_VALUE",
      data: {
        type: "STRING",
        value: "{{ output[0].type }}",
      },
    };

    const templatingNode = templatingNodeFactory({
      inputReferences: [
        {
          referenceId: promptNode.data.arrayOutputId,
          referenceNodeId: promptNode.id,
        },
      ],
      template: template,
    });

    const templatingNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: templatingNode,
    })) as TemplatingNodeContext;

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
});

describe("Non-existent Subworkflow Deployment Node referenced by Templating Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;
  beforeEach(async () => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();
    vi.spyOn(
      WorkflowDeploymentsClient.prototype,
      "workflowDeploymentHistoryItemRetrieve"
    ).mockResolvedValue({
      name: "test-deployment",
      outputVariables: [{ id: "1", key: "output-1", type: "STRING" }],
    } as unknown as WorkflowDeploymentHistoryItem);

    const subworkflowNodeData = subworkflowDeploymentNodeDataFactory();

    await createNodeContext({
      workflowContext: workflowContext,
      nodeData: subworkflowNodeData,
    });

    const promptNode = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
    });

    await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    });

    const template: ConstantValuePointer = {
      type: "CONSTANT_VALUE",
      data: {
        type: "STRING",
        value: "{{ output[0].type }}",
      },
    };

    const templatingNode = templatingNodeFactory({
      inputReferences: [
        {
          referenceId: promptNode.data.arrayOutputId,
          referenceNodeId: promptNode.id,
        },
        {
          referenceId: "some-non-existent-subworkflow-output-id",
          referenceNodeId: subworkflowNodeData.id,
        },
      ],
      template: template,
    });

    const templatingNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: templatingNode,
    })) as TemplatingNodeContext;

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
});
