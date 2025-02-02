import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuid } from "uuid";
import { SecretTypeEnum, WorkspaceSecretRead } from "vellum-ai/api";
import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { beforeEach, describe } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  apiNodeFactory,
  ApiNodeFactoryProps,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ApiNodeContext } from "src/context/node-context/api-node";
import { ApiNode } from "src/generators/nodes/api-node";

describe("ApiNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ApiNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "5f64210f-ec43-48ce-ae40-40a9ba4c4c11",
          key: "additional_header_value",
          type: "STRING",
        },
        workflowContext,
      })
    );
    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "b81c5c88-9528-47d0-8106-14a75520ed47",
          key: "additional_header_value",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  const mockWorkspaceSecretDefinition = (workspaceSecret: {
    id: string;
    name: string;
  }): WorkspaceSecretRead => ({
    id: workspaceSecret.id,
    name: workspaceSecret.name,
    modified: new Date(),
    label: "mocked-workspace-secret-label",
    secretType: SecretTypeEnum.UserDefined,
  });

  const createNode = async ({
    workspaceSecrets,
    ...apiNodeProps
  }: {
    workspaceSecrets: { id: string; name: string }[];
  } & ApiNodeFactoryProps) => {
    const workspaceSecretIdByName = Object.fromEntries(
      workspaceSecrets.map(({ id, name }) => [name, id])
    );
    const workspaceSecretNameById = Object.fromEntries(
      workspaceSecrets.map(({ id, name }) => [id, name])
    );
    vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockImplementation(
      async (idOrName) => {
        const id = workspaceSecretIdByName[idOrName];
        if (id) {
          return mockWorkspaceSecretDefinition({
            id,
            name: idOrName,
          });
        }

        const name = workspaceSecretNameById[idOrName];
        if (name) {
          return mockWorkspaceSecretDefinition({
            id: idOrName,
            name,
          });
        }

        throw new Error(`Workspace secret ${idOrName} not found`);
      }
    );

    const nodeData = apiNodeFactory(apiNodeProps);

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ApiNodeContext;

    return new ApiNode({
      workflowContext,
      nodeContext,
    });
  };

  describe("basic auth secret node", () => {
    it.each([{ id: "1234", name: "test-secret" }])(
      "secret ids should show names",
      async (workspaceSecret: { id: string; name: string }) => {
        node = await createNode({
          workspaceSecrets: [workspaceSecret],
          bearerToken: {
            id: uuid(),
            key: "bearer_token_value",
            value: {
              rules: [
                {
                  type: "WORKSPACE_SECRET",
                  data: {
                    type: "STRING",
                    workspaceSecretId: workspaceSecret.id,
                  },
                },
              ],
              combinator: "OR",
            },
          },
          apiKeyHeaderValue: {
            id: uuid(),
            key: "api_key_header_value",
            value: {
              rules: [
                {
                  type: "WORKSPACE_SECRET",
                  data: {
                    type: "STRING",
                    workspaceSecretId: workspaceSecret.id,
                  },
                },
              ],
              combinator: "OR",
            },
          },
        });
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
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

  describe("reject on error enabled", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory({
        errorOutputId: "af589f73-effe-4a80-b48f-fb912ac6ce67",
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
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
});
