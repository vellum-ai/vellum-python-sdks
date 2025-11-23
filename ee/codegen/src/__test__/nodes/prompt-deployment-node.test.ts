import { v4 as uuidv4 } from "uuid";
import { Deployments as PromptDeploymentReleaseClient } from "vellum-ai/api/resources/deployments/client/Client";
import { PromptDeploymentRelease } from "vellum-ai/api/types/PromptDeploymentRelease";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  nodeInputFactory,
  promptDeploymentNodeDataFactory,
} from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { createNodeContext, WorkflowContext } from "src/context";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { Writer } from "src/generators/extensions/writer";
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
      writer = new Writer();
      workflowContext = workflowContextFactory();
      const nodeData = promptDeploymentNodeDataFactory().build();

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
      writer = new Writer();
      workflowContext = workflowContextFactory();

      const nodeData = promptDeploymentNodeDataFactory({
        mlModelFallbacks: ["model1"],
      }).build();

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
        "retrievePromptDeploymentRelease"
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
      const nodeData = promptDeploymentNodeDataFactory().build();

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
          id: randomJsonOutputId,
          name: "json",
          type: "JSON",
        },
      ];
      writer = new Writer();
      workflowContext = workflowContextFactory();
      const nodeData = promptDeploymentNodeDataFactory()
        .withOutputs(nodeOutputs)
        .build();

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

  describe("basic with node inputs and the prompt_inputs attribute defined", () => {
    it("should generate node file prioritizing the latter", async () => {
      const workflowContext = workflowContextFactory();
      const writer = new Writer();

      const textStateVariableId = uuidv4();
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: textStateVariableId,
            key: "text",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const nodeData = promptDeploymentNodeDataFactory({
        inputs: [
          nodeInputFactory({
            id: uuidv4(),
            key: "foo",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "bar",
              },
            },
          }),
        ],
      })
        .withAttributes([
          {
            id: uuidv4(),
            name: "prompt_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  key: "text",
                  value: {
                    type: "WORKFLOW_STATE",
                    stateVariableId: textStateVariableId,
                  },
                },
              ],
            },
          },
        ])
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as PromptDeploymentNodeContext;

      const node = new PromptDeploymentNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
