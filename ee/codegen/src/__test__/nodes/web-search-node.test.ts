import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  nodePortFactory,
  webSearchNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import { NodePort } from "src/types/vellum";

describe("WebSearchNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "search-query-input-id",
          key: "query",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "web-search-port-id",
        }),
      ];
      const nodeData = webSearchNodeFactory({ nodePorts: nodePortData });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
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

  describe("with custom attributes", () => {
    it("should generate a web search node with workflow input", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "web-search-port-id",
        }),
      ];

      const nodeData = webSearchNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [
          {
            id: "custom-query-id",
            name: "query",
            value: {
              type: "WORKFLOW_INPUT",
              inputVariableId: "search-query-input-id",
            },
          },
          {
            id: "custom-api-key-id",
            name: "api_key",
            value: {
              type: "ENVIRONMENT_VARIABLE",
              environmentVariable: "CUSTOM_SERP_KEY",
            },
          },
          {
            id: "custom-num-results-id",
            name: "num_results",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "NUMBER", value: 5 },
            },
          },
          {
            id: "custom-location-id",
            name: "location",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "California" },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const testNode = new GenericNode({
        workflowContext,
        nodeContext,
      });

      testNode.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("value type variations", () => {
    it("should handle NODE_OUTPUT for query parameter", async () => {
      // Add a mock node output for the test
      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "previous-node-output-id",
            key: "search_results",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const nodeData = webSearchNodeFactory({
        nodeAttributes: [
          {
            id: "query-from-node-output",
            name: "query",
            value: {
              type: "NODE_OUTPUT",
              nodeId: "previous-search-node",
              nodeOutputId: "previous-node-output-id",
            },
          },
          {
            id: "api-key-secret",
            name: "api_key",
            value: {
              type: "ENVIRONMENT_VARIABLE",
              environmentVariable: "SERP_API_KEY",
            },
          },
          {
            id: "num-results-constant",
            name: "num_results",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "NUMBER", value: 5 },
            },
          },
          {
            id: "location-constant",
            name: "location",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "New York" },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const testNode = new GenericNode({
        workflowContext,
        nodeContext,
      });

      testNode.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("parameter validation", () => {
    it("should handle string to number conversion for num_results", async () => {
      const nodeData = webSearchNodeFactory({
        nodeAttributes: [
          {
            id: "query-constant",
            name: "query",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "AI news" },
            },
          },
          {
            id: "num-results-string",
            name: "num_results",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "15" },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const testNode = new GenericNode({
        workflowContext,
        nodeContext,
      });

      testNode.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("edge cases", () => {
    it("should handle special characters in query", async () => {
      const nodeData = webSearchNodeFactory({
        nodeAttributes: [
          {
            id: "query-special-chars",
            name: "query",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: 'AI & ML "deep learning" (2024)',
              },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const testNode = new GenericNode({
        workflowContext,
        nodeContext,
      });

      testNode.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle minimal configuration with only required query", async () => {
      const nodeData = webSearchNodeFactory({
        nodeAttributes: [
          {
            id: "query-only",
            name: "query",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "minimal search" },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const testNode = new GenericNode({
        workflowContext,
        nodeContext,
      });

      testNode.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
