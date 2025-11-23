import { v4 as uuidv4 } from "uuid";
import { WorkflowDeploymentRelease } from "vellum-ai/api";
import { Deployments as PromptDeploymentReleaseClient } from "vellum-ai/api/resources/deployments/client/Client";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { WorkflowDeployments as WorkflowReleaseClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { MetricDefinitionHistoryItem } from "vellum-ai/api/types/MetricDefinitionHistoryItem";
import { PromptDeploymentRelease } from "vellum-ai/api/types/PromptDeploymentRelease";
import { beforeEach, expect, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  guardrailNodeDataFactory,
  inlinePromptNodeDataInlineVariantFactory,
  inlineSubworkflowNodeDataFactory,
  nodeInputFactory,
  promptDeploymentNodeDataFactory,
  subworkflowDeploymentNodeDataFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { Writer } from "src/generators/extensions/writer";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import {
  AdornmentNode,
  NodeAttribute as NodeAttributeType,
  NodeOutput as NodeOutputType,
} from "src/types/vellum";

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
    }).build();

    await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    });

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: errorOutputId,
      inputReferenceNodeId: promptNode.id,
    }).build();

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
    vi.spyOn(
      PromptDeploymentReleaseClient.prototype,
      "retrievePromptDeploymentRelease"
    ).mockResolvedValue({
      id: "947cc337-9a53-4c12-9a38-4f65c04c6317",
      created: new Date(),
      environment: {
        id: "mocked-environment-id",
        name: "mocked-environment-name",
        label: "mocked-environment-label",
      },
      createdBy: {
        id: "mocked-created-by-id",
        email: "mocked-created-by-email",
      },
      promptVersion: {
        id: "mocked-prompt-release-id",
      },
      deployment: {
        name: "some-unique-deployment-name",
      },
      releaseTags: [
        {
          name: "mocked-release-tag-name",
          source: "USER",
        },
      ],
      reviews: [
        {
          id: "mocked-release-review-id",
          created: new Date(),
          reviewer: {
            id: "mocked-reviewer-id",
          },
          state: "APPROVED",
        },
      ],
    } as unknown as PromptDeploymentRelease);
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
    }).build();

    await createNodeContext({
      workflowContext,
      nodeData: promptDeploymentNode,
    });

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: outputId,
      inputReferenceNodeId: promptDeploymentNode.id,
    }).build();

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
    }).build();

    (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;

    const templatingNode = templatingNodeFactory({
      id: "46e221ab-a749-41a2-9242-b1f5bf31f3a5",
      sourceHandleId: "6ee2c814-d0a5-4ec9-83b6-45156e2f22c4",
      targetHandleId: "3960c8e1-9baa-4b9c-991d-e399d16a45aa",
      inputs: [
        {
          id: "9feb7b5e-5947-496d-b56f-1e2627730796",
          key: "text",
          value: {
            rules: [
              {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: promptNode.id,
                  outputId: promptNode.data.outputId,
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
          key: "template",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "{{ output[0].type }}",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ],
    }).build();

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
      WorkflowReleaseClient.prototype,
      "retrieveWorkflowDeploymentRelease"
    ).mockResolvedValue({
      id: "mocked-workflow-deployment-history-item-id",
      created: new Date(),
      environment: {
        id: "mocked-environment-id",
        name: "mocked-environment-name",
        label: "mocked-environment-label",
      },
      createdBy: {
        id: "mocked-created-by-id",
        email: "mocked-created-by-email",
      },
      workflowVersion: {
        id: "mocked-workflow-release-id",
        inputVariables: [],
        outputVariables: [{ id: "1", key: "output-1", type: "STRING" }],
      },
      deployment: {
        name: "test-deployment",
      },
      releaseTags: [
        {
          name: "mocked-release-tag-name",
          source: "USER",
        },
      ],
      reviews: [
        {
          id: "mocked-release-review-id",
          created: new Date(),
          reviewer: {
            id: "mocked-reviewer-id",
          },
          state: "APPROVED",
        },
      ],
    } as unknown as WorkflowDeploymentRelease);

    const subworkflowNodeData = subworkflowDeploymentNodeDataFactory().build();

    await createNodeContext({
      workflowContext: workflowContext,
      nodeData: subworkflowNodeData,
    });

    const promptNode = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
    }).build();

    await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    });

    const templatingNode = templatingNodeFactory({
      id: "46e221ab-a749-41a2-9242-b1f5bf31f3a5",
      sourceHandleId: "6ee2c814-d0a5-4ec9-83b6-45156e2f22c4",
      targetHandleId: "3960c8e1-9baa-4b9c-991d-e399d16a45aa",
      inputs: [
        {
          id: "9feb7b5e-5947-496d-b56f-1e2627730796",
          key: "text",
          value: {
            rules: [
              {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: promptNode.id,
                  outputId: promptNode.data.outputId,
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "9feb7b5e-5947-496d-b56f-1e2627730796",
          key: "output",
          value: {
            rules: [
              {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: subworkflowNodeData.id,
                  outputId: "some-non-existent-subworkflow-output-id",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
          key: "template",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "{{ output[0].type }}",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ],
    }).build();

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

  it("workflow context should have the error logged", async () => {
    const errors = workflowContext.getErrors();
    expect(errors).toHaveLength(1);

    const error = errors[0];
    expect(error?.severity).toBe("WARNING");
    expect(error?.message).toContain(
      "Could not find Subworkflow Deployment Output with id some-non-existent-subworkflow-output-id"
    );
  });
});

describe("InlinePromptNode json output referenced by TemplatingNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;
  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeOutputs: NodeOutputType[] = [
      {
        id: uuidv4(),
        name: "json",
        type: "JSON",
      },
    ];
    const promptNode = inlinePromptNodeDataInlineVariantFactory({})
      .withOutputs(nodeOutputs)
      .build();

    (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;

    const templatingNode = templatingNodeFactory({
      inputs: [
        nodeInputFactory({
          id: "9feb7b5e-5947-496d-b56f-1e2627730796",
          key: "var_1",
          value: {
            type: "NODE_OUTPUT",
            data: {
              nodeId: promptNode.id,
              outputId: nodeOutputs[0]?.id ?? uuidv4(),
            },
          },
        }),
        nodeInputFactory({
          id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
          key: "template",
          value: {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "{{ output[0].type }}",
            },
          },
        }),
      ],
    }).build();

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
});

describe("PromptDeploymentNode json output referenced by TemplatingNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;
  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    vi.spyOn(
      PromptDeploymentReleaseClient.prototype,
      "retrievePromptDeploymentRelease"
    ).mockResolvedValue({
      id: "947cc337-9a53-4c12-9a38-4f65c04c6317",
      created: new Date(),
      environment: {
        id: "mocked-environment-id",
        name: "mocked-environment-name",
        label: "mocked-environment-label",
      },
      createdBy: {
        id: "mocked-created-by-id",
        email: "mocked-created-by-email",
      },
      promptVersion: {
        id: "mocked-prompt-release-id",
      },
      deployment: {
        name: "some-unique-deployment-name",
      },
      releaseTags: [
        {
          name: "mocked-release-tag-name",
          source: "USER",
        },
      ],
      reviews: [
        {
          id: "mocked-release-review-id",
          created: new Date(),
          reviewer: {
            id: "mocked-reviewer-id",
          },
          state: "APPROVED",
        },
      ],
    } as unknown as PromptDeploymentRelease);

    const nodeOutputs: NodeOutputType[] = [
      {
        id: uuidv4(),
        name: "json",
        type: "JSON",
      },
    ];
    const promptDeploymentNode = promptDeploymentNodeDataFactory()
      .withOutputs(nodeOutputs)
      .build();

    await createNodeContext({
      workflowContext,
      nodeData: promptDeploymentNode,
    });

    const templatingNode = templatingNodeFactory({
      inputs: [
        nodeInputFactory({
          id: "9feb7b5e-5947-496d-b56f-1e2627730796",
          key: "var_1",
          value: {
            type: "NODE_OUTPUT",
            data: {
              nodeId: promptDeploymentNode.id,
              outputId: nodeOutputs[0]?.id ?? uuidv4(),
            },
          },
        }),
        nodeInputFactory({
          id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
          key: "template",
          value: {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "{{ var_1.type }}",
            },
          },
        }),
      ],
    }).build();

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
});

describe("Inline Subworkflow Try adornment referenced by Conditional Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const tryAdornment: AdornmentNode = {
      id: "ae49ef72-6ad7-441a-a20d-76c71ad851ef",
      label: "TryNodeLabel",
      base: {
        name: "TryNode",
        module: ["vellum", "workflows", "nodes", "core", "try_node", "node"],
      },
      attributes: [],
    };

    const subworkflowNode = inlineSubworkflowNodeDataFactory({
      label: "Subworkflow with Try",
      nodes: [templatingNodeFactory({ label: "Inner node" }).build()],
    })
      .withAdornments([tryAdornment])
      .build();

    await createNodeContext({
      workflowContext,
      nodeData: subworkflowNode,
    });

    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: tryAdornment.id,
      inputReferenceNodeId: subworkflowNode.id,
    }).build();

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
});

describe("GuardrailNode with score output as type STRING referenced by Conditional Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    vi.spyOn(
      MetricDefinitionsClient.prototype,
      "metricDefinitionHistoryItemRetrieve"
    ).mockResolvedValue({
      id: "mocked-metric-output-id",
      label: "mocked-metric-output-label",
      name: "mocked-metric-output-name",
      description: "mocked-metric-output-description",
      outputVariables: [
        { id: "score-output-id", key: "score", type: "STRING" },
      ],
    } as unknown as MetricDefinitionHistoryItem);

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "a6ef8809-346e-469c-beed-2e5c4e9844c5",
          key: "expected",
          type: "STRING",
        },
        workflowContext,
      })
    );

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "1472503c-1662-4da9-beb9-73026be90c68",
          key: "actual",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const guardrailNode = guardrailNodeDataFactory({
      inputs: [
        {
          id: "3f917af8-03a4-4ca4-8d40-fa662417fe9c",
          key: "expected",
          value: {
            rules: [
              {
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "a6ef8809-346e-469c-beed-2e5c4e9844c5",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "bed55ada-923e-46ef-8340-1a5b0b563dc1",
          key: "actual",
          value: {
            rules: [
              {
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "1472503c-1662-4da9-beb9-73026be90c68",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ],
    }).build();

    await createNodeContext({
      workflowContext,
      nodeData: guardrailNode,
    });

    // Create a custom conditional node with numeric comparison value
    const conditionalNode = conditionalNodeFactory({
      inputReferenceId: "score-output-id",
      inputReferenceNodeId: guardrailNode.id,
      inputs: [
        {
          id: "2cb6582e-c329-4952-8598-097830b766c7",
          key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.field",
          value: {
            rules: [
              {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: guardrailNode.id,
                  outputId: "score-output-id",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
          key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "1",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ],
    }).build();

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
});

describe("InlinePromptNode with prompt inputs generating lazy reference", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: InlinePromptNode;

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

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "f656599c-b8be-4a1b-9935-3240018522bc",
          key: "chat_history",
          type: "CHAT_HISTORY",
        },
        workflowContext,
      })
    );

    const templatingNodeId = uuidv4();
    const templatingNodeOutputId = uuidv4();

    const promptInputAttributes: NodeAttributeType[] = [
      {
        id: uuidv4(),
        name: "prompt_inputs",
        value: {
          type: "DICTIONARY_REFERENCE",
          entries: [
            {
              key: "text",
              value: {
                type: "NODE_OUTPUT",
                nodeId: templatingNodeId,
                nodeOutputId: templatingNodeOutputId,
              },
            },
          ],
        },
      },
    ];

    const promptNode = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
    })
      .withAttributes(promptInputAttributes)
      .build();

    const promptNodeContext = (await createNodeContext({
      workflowContext,
      nodeData: promptNode,
    })) as InlinePromptNodeContext;

    const templatingNode = templatingNodeFactory({
      id: templatingNodeId,
      outputId: templatingNodeOutputId,
    }).build();

    await createNodeContext({
      workflowContext,
      nodeData: templatingNode,
    });

    node = new InlinePromptNode({
      workflowContext,
      nodeContext: promptNodeContext,
    });
  });

  it("getNodeFile generates lazy reference", async () => {
    node.getNodeFile().write(writer);
    const output = await writer.toStringFormatted();
    expect(output).toContain("LazyReference");
    expect(output).toMatchSnapshot();
  });
});
