import { Writer } from "@fern-api/python-ast/core/Writer";
import { DeploymentHistoryItem } from "vellum-ai/api";
import { Deployments as DeploymentsClient } from "vellum-ai/api/resources/deployments/client/Client";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { promptDeploymentNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { PromptDeploymentNode } from "src/generators/nodes/prompt-deployment-node";

describe("PromptDeploymentNode", () => {
  let workflowContext: WorkflowContext;
  let node: PromptDeploymentNode;
  let writer: Writer;

  describe("basic", () => {
    beforeEach(async () => {
      vi.spyOn(
        DeploymentsClient.prototype,
        "deploymentHistoryItemRetrieve"
      ).mockResolvedValue({
        id: "some-id",
        deploymentId: "947cc337-9a53-4c12-9a38-4f65c04c6317",
        name: "some-unique-deployment-name",
      } as unknown as DeploymentHistoryItem);
      writer = new Writer();
      workflowContext = workflowContextFactory();
      const nodeData = promptDeploymentNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as PromptDeploymentNodeContext;

      node = new PromptDeploymentNode({
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

  describe("fallback models", () => {
    beforeEach(async () => {
      vi.spyOn(
        DeploymentsClient.prototype,
        "deploymentHistoryItemRetrieve"
      ).mockResolvedValue({
        id: "some-id",
        deploymentId: "947cc337-9a53-4c12-9a38-4f65c04c6317",
        name: "some-unique-deployment-name",
      } as unknown as DeploymentHistoryItem);
      writer = new Writer();
      workflowContext = workflowContextFactory();

      const nodeData = promptDeploymentNodeDataFactory({
        fallbackModels: ["model1"],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as PromptDeploymentNodeContext;

      node = new PromptDeploymentNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile should fail`, async () => {
      expect(() => node.getNodeFile().write(writer)).toThrowError(
        "Fallback models not currently support"
      );
    });
  });

  describe("no prompt deployment found", () => {
    beforeEach(async () => {
      vi.spyOn(
        DeploymentsClient.prototype,
        "deploymentHistoryItemRetrieve"
      ).mockRejectedValue(
        new VellumError({
          message: "Deployment not found",
          body: {
            detail: "Could not find prompt deployment",
          },
        })
      );
      writer = new Writer();
      workflowContext = workflowContextFactory();
      const nodeData = promptDeploymentNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as PromptDeploymentNodeContext;

      node = new PromptDeploymentNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
