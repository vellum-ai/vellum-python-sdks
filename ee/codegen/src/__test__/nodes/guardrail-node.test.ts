import { Writer } from "@fern-api/python-ast/core/Writer";
import { MetricDefinitionHistoryItem } from "vellum-ai/api";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { guardrailNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GuardrailNodeContext } from "src/context/node-context/guardrail-node";
import { GuardrailNode } from "src/generators/nodes/guardrail-node";

describe("GuardrailNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

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
          id: "abed55ada-923e-46ef-8340-1a5b0b563dc1",
          key: "actual",
          type: "STRING",
        },
        workflowContext,
      })
    );

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "1472503c-1662-4da9-beb9-73026be90c68",
          key: "output",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  const mockMetricDefinition = (
    outputVariables: { id: string; key: string; type: string }[]
  ) => ({
    id: "mocked-metric-output-id",
    label: "mocked-metric-output-label",
    name: "mocked-metric-output-name",
    description: "mocked-metric-output-description",
    outputVariables,
  });

  const createNode = async ({
    errorOutputId,
    outputVariables,
  }: {
    errorOutputId?: string;
    outputVariables: { id: string; key: string; type: string }[];
  }) => {
    vi.spyOn(
      MetricDefinitionsClient.prototype,
      "metricDefinitionHistoryItemRetrieve"
    ).mockResolvedValue(
      mockMetricDefinition(
        outputVariables
      ) as unknown as MetricDefinitionHistoryItem
    );
    const nodeData = guardrailNodeDataFactory({ errorOutputId });

    const nodeContext = createNodeContext({
      workflowContext,
      nodeData,
    }) as GuardrailNodeContext;
    workflowContext.addNodeContext(nodeContext);
    await nodeContext.buildProperties();

    return new GuardrailNode({
      workflowContext: workflowContext,
      nodeContext,
    });
  };

  describe("basic", () => {
    it.each([
      [
        "single output variable",
        [{ id: "mocked-input-id", key: "score", type: "NUMBER" }],
      ],
      [
        "multiple output variables",
        [
          { id: "mocked-input-id-1", key: "score1", type: "NUMBER" },
          { id: "mocked-input-id-2", key: "score2", type: "NUMBER" },
        ],
      ],
    ])("getNodeFile - %s", async (_, outputVariables) => {
      const node = await createNode({ outputVariables });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it.each([
      [
        "single output variable",
        [{ id: "mocked-input-id", key: "score", type: "NUMBER" }],
      ],
      [
        "multiple output variables",
        [
          { id: "mocked-input-id-1", key: "score1", type: "NUMBER" },
          { id: "mocked-input-id-2", key: "score2", type: "NUMBER" },
        ],
      ],
    ])("getNodeDisplayFile - %s", async (_, outputVariables) => {
      const node = await createNode({ outputVariables });

      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("reject on error enabled", () => {
    it("getNodeFile", async () => {
      const node = await createNode({
        errorOutputId: "38361ff1-c826-49b8-aa8d-28179c3684cc",
        outputVariables: [
          { id: "mocked-input-id-1", key: "score1", type: "NUMBER" },
          { id: "mocked-input-id-2", key: "score2", type: "NUMBER" },
        ],
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      const node = await createNode({
        errorOutputId: "38361ff1-c826-49b8-aa8d-28179c3684cc",
        outputVariables: [
          { id: "mocked-input-id-1", key: "score1", type: "NUMBER" },
          { id: "mocked-input-id-2", key: "score2", type: "NUMBER" },
        ],
      });

      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
