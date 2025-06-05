import { Writer } from "@fern-api/python-ast/core/Writer";
import { WorkflowDeploymentRelease } from "vellum-ai/api";
import { ReleaseReviews as WorkflowReleaseClient } from "vellum-ai/api/resources/releaseReviews/client/Client";
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
          outputVariables: [
            { id: "1", key: "output-1", type: "STRING" },
            { id: "2", key: "output-2", type: "NUMBER" },
          ],
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

      const nodeData = subworkflowDeploymentNodeDataFactory().build();

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
        WorkflowReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory().build();

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
        WorkflowReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory().build();

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
        WorkflowReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
      ).mockRejectedValue(
        new VellumError({
          body: {
            detail: "No Workflow Deployment found.",
          },
        })
      );

      const nodeData = subworkflowDeploymentNodeDataFactory().build();

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

      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(2);

      expect(errors[0]?.message).toContain("No Workflow Deployment found.");
      expect(errors[0]?.severity).toBe("WARNING");

      expect(errors[1]?.message).toContain(
        "Failed to generate `output_display` for Subworkflow Node"
      );
      expect(errors[1]?.severity).toBe("WARNING");
    });
  });

  describe("case preservation", () => {
    it("should preserve case in output names like fooBAR", async () => {
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
          outputVariables: [
            { id: "test-output-id", key: "fooBAR", type: "STRING" },
          ],
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

      const nodeData = subworkflowDeploymentNodeDataFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as SubworkflowDeploymentNodeContext;

      const outputName = nodeContext.getNodeOutputNameById("test-output-id");
      expect(outputName).toBe("fooBAR");
    });
  });
});
