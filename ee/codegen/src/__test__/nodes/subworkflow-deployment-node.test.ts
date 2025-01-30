import { Writer } from "@fern-api/python-ast/core/Writer";
import { WorkflowDeploymentHistoryItem } from "vellum-ai/api";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { subworkflowDeploymentNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { SubworkflowDeploymentNode } from "src/generators/nodes/subworkflow-deployment-node";

describe("SubworkflowDeploymentNode", () => {
  let workflowContext: WorkflowContext;
  let node: SubworkflowDeploymentNode;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      vi.spyOn(
        WorkflowDeploymentsClient.prototype,
        "workflowDeploymentHistoryItemRetrieve"
      ).mockResolvedValue({
        name: "test-deployment",
        outputVariables: [
          { id: "1", key: "output-1", type: "STRING" },
          { id: "2", key: "output-2", type: "NUMBER" },
        ],
      } as unknown as WorkflowDeploymentHistoryItem);

      const nodeData = subworkflowDeploymentNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as SubworkflowDeploymentNodeContext;

      node = new SubworkflowDeploymentNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("failure", () => {
    it(`should throw an error we can handle if the workflow deployment history item is not found`, async () => {
      vi.spyOn(
        WorkflowDeploymentsClient.prototype,
        "workflowDeploymentHistoryItemRetrieve"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory();

      await expect(
        createNodeContext({
          workflowContext,
          nodeData,
        })
      ).rejects.toThrow(
        new NodeDefinitionGenerationError("No Workflow Deployment found.")
      );
    });

    it(`should generate subworkflow deployment nodes as much as possible for non strict workflow contexts`, async () => {
      const workflowContext = workflowContextFactory({
        strict: false,
      });

      vi.spyOn(
        WorkflowDeploymentsClient.prototype,
        "workflowDeploymentHistoryItemRetrieve"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as SubworkflowDeploymentNodeContext;

      node = new SubworkflowDeploymentNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it(`should generate subworkflow deployment node display as much as possible for non strict workflow contexts`, async () => {
      const workflowContext = workflowContextFactory({
        strict: false,
      });

      vi.spyOn(
        WorkflowDeploymentsClient.prototype,
        "workflowDeploymentHistoryItemRetrieve"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as SubworkflowDeploymentNodeContext;

      node = new SubworkflowDeploymentNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
