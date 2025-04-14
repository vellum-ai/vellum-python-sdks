import { Writer } from "@fern-api/python-ast/core/Writer";
import { ReleaseReviews as PromptDeploymentReleaseClient } from "vellum-ai/api/resources/releaseReviews/client/Client";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { promptDeploymentNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { PromptDeploymentNode } from "src/generators/nodes/prompt-deployment-node";
import { NodeOutput as NodeOutputType } from "src/types/vellum";

describe("PromptDeploymentNode", () => {
  let workflowContext: WorkflowContext;
  let node: PromptDeploymentNode;
  let writer: Writer;

  describe("basic", () => {
    beforeEach(async () => {
      vi.spyOn(
        PromptDeploymentReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
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
        workflowVersion: {
          id: "mocked-prompt-release-id",
          inputVariables: [],
          outputVariables: [],
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
      });
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
        PromptDeploymentReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
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
        workflowVersion: {
          id: "mocked-prompt-release-id",
          inputVariables: [],
          outputVariables: [],
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
      });
      writer = new Writer();
      workflowContext = workflowContextFactory();

      const nodeData = promptDeploymentNodeDataFactory({
        mlModelFallbacks: ["model1"],
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
    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("no prompt deployment found", () => {
    beforeEach(async () => {
      vi.spyOn(
        PromptDeploymentReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
      ).mockRejectedValue(
        new VellumError({
          message: "Deployment not found",
          body: {
            detail: "Could not find prompt deployment",
          },
        })
      );
      writer = new Writer();
      workflowContext = workflowContextFactory({ strict: false });
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

  describe("with json output id defined", async () => {
    const randomJsonOutputId = "82c3d131-fe28-4f48-93c0-34ecf5a2a703";
    let node: PromptDeploymentNode;
    beforeEach(async () => {
      vi.spyOn(
        PromptDeploymentReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
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
        workflowVersion: {
          id: "mocked-prompt-release-id",
          inputVariables: [],
          outputVariables: [],
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
      });
      const nodeOutputs: NodeOutputType[] = [
        {
          id: randomJsonOutputId,
          name: "json",
          type: "JSON",
        },
      ];
      writer = new Writer();
      workflowContext = workflowContextFactory();
      const nodeData = promptDeploymentNodeDataFactory({
        outputs: nodeOutputs,
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

    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
