import { WorkflowDeploymentRelease } from "vellum-ai/api";
import { WorkflowDeployments as WorkflowReleaseClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  entrypointNodeDataFactory,
  subworkflowDeploymentNodeDataFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import { OutputVariableContext } from "src/context/output-variable-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { Writer } from "src/generators/extensions/writer";
import { SubworkflowDeploymentNode } from "src/generators/nodes/subworkflow-deployment-node";
import { DictionaryWorkflowReference } from "src/types/vellum";

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

  describe("accessor expression inputs", () => {
    it("should generate code for accessor expression inputs", async () => {
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
          outputVariables: [],
        },
        deployment: {
          name: "test-deployment",
        },
        releaseTags: [],
        reviews: [],
      } as unknown as WorkflowDeploymentRelease);

      // Use DICTIONARY_REFERENCE for subworkflow_inputs attribute with nested expressions
      const subworkflowInputsAttr: DictionaryWorkflowReference = {
        type: "DICTIONARY_REFERENCE",
        entries: [
          {
            id: "entry-id-1",
            key: "user_name",
            value: {
              type: "BINARY_EXPRESSION",
              operator: "accessField",
              lhs: {
                type: "WORKFLOW_INPUT",
                inputVariableId: "test-input-variable-id",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "name",
                },
              },
            },
          },
        ],
      };

      const nodeData = subworkflowDeploymentNodeDataFactory({
        attributes: [
          {
            id: "subworkflow-inputs-attr-id",
            name: "subworkflow_inputs",
            value: subworkflowInputsAttr,
          },
        ],
      }).build();

      workflowContext = workflowContextFactory();
      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "test-input-variable-id",
            key: "item",
            type: "JSON",
          },
          workflowContext,
        })
      );

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

  describe("workflow output variable ID lookup", () => {
    it("should resolve output by workflow output variable ID when key matches deployed workflow output", async () => {
      /**
       * Tests that when a TERMINAL node references a SUBWORKFLOW deployment node's output
       * using the workflow's output variable ID (not the deployed workflow's output variable ID),
       * the output name is correctly resolved by matching keys.
       */

      // GIVEN a workflow context with an output variable that has a different ID than the deployed workflow
      const workflowOutputVariableId = "workflow-output-feedback-id";
      const deployedOutputVariableId = "deployed-output-feedback-id";
      const sharedOutputKey = "feedback";

      const workflowContextWithOutputVar = workflowContextFactory({
        workflowRawData: {
          nodes: [entrypointNodeDataFactory()],
          edges: [],
        },
      });

      // AND the workflow has an output variable with the shared key
      const outputVariableContext = new OutputVariableContext({
        outputVariableData: {
          id: workflowOutputVariableId,
          key: sharedOutputKey,
          type: "STRING",
        },
        workflowContext: workflowContextWithOutputVar,
      });
      workflowContextWithOutputVar.addOutputVariableContext(
        outputVariableContext
      );

      // AND the deployed workflow has an output variable with the same key but different ID
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
            {
              id: deployedOutputVariableId,
              key: sharedOutputKey,
              type: "STRING",
            },
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

      // WHEN we create the node context
      const nodeContext = (await createNodeContext({
        workflowContext: workflowContextWithOutputVar,
        nodeData,
      })) as SubworkflowDeploymentNodeContext;

      // THEN we should be able to look up the output by the deployed workflow's output variable ID
      const outputNameByDeployedId = nodeContext.getNodeOutputNameById(
        deployedOutputVariableId
      );
      expect(outputNameByDeployedId).toBe(sharedOutputKey);

      // AND we should also be able to look up the output by the workflow's output variable ID
      const outputNameByWorkflowId = nodeContext.getNodeOutputNameById(
        workflowOutputVariableId
      );
      expect(outputNameByWorkflowId).toBe(sharedOutputKey);

      // AND we should be able to look up the type by the workflow's output variable ID
      const outputTypeByWorkflowId = nodeContext.getNodeOutputTypeById(
        workflowOutputVariableId
      );
      expect(outputTypeByWorkflowId).toBe("STRING");
    });
  });
});
