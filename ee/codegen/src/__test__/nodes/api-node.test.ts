import { v4 as uuidv4 } from "uuid";
import { SecretTypeEnum, WorkspaceSecretRead } from "vellum-ai/api";
import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors/VellumError";
import { beforeEach, describe } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  apiNodeFactory,
  ApiNodeFactoryProps,
  nodeInputFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ApiNodeContext } from "src/context/node-context/api-node";
import { EntityNotFoundError } from "src/generators/errors";
import { Writer } from "src/generators/extensions/writer";
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
      // @ts-ignore
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

    const nodeData = apiNodeFactory(apiNodeProps).build();

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ApiNodeContext;

    return new ApiNode({
      workflowContext,
      nodeContext,
    });
  };

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory().build();

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

  describe("basic api node", () => {
    it("should generate empty string when url is missing", async () => {
      const nodeData = apiNodeFactory({
        url: null,
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should not generate method field when method is GET", async () => {
      const nodeData = apiNodeFactory({
        method: "GET",
      }).build();
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should not generate body field when body is None", async () => {
      const nodeData = apiNodeFactory({
        body: null,
      }).build();
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic auth secret node", () => {
    it.each([{ id: "1234", name: "test-secret" }])(
      "secret ids should show names",
      async (workspaceSecret: { id: string; name: string }) => {
        node = await createNode({
          workspaceSecrets: [workspaceSecret],
          bearerToken: nodeInputFactory({
            key: "bearer_token_value",
            value: {
              type: "WORKSPACE_SECRET",
              data: {
                type: "STRING",
                workspaceSecretId: workspaceSecret.id,
              },
            },
          }),
          apiKeyHeaderValue: nodeInputFactory({
            key: "api_key_header_value",
            value: {
              type: "WORKSPACE_SECRET",
              data: {
                type: "STRING",
                workspaceSecretId: workspaceSecret.id,
              },
            },
          }),
        });
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );

    it("should generate Workspace secrets for header values", async () => {
      const workspaceSecretId = uuidv4();
      node = await createNode({
        workspaceSecrets: [{ id: workspaceSecretId, name: "test-secret" }],
        additionalHeaders: [
          {
            key: nodeInputFactory({
              key: "test-key",
              value: {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "X-Secret-Key",
                },
              },
            }),
            value: nodeInputFactory({
              key: "test-value",
              value: {
                type: "WORKSPACE_SECRET",
                data: {
                  type: "STRING",
                  workspaceSecretId: workspaceSecretId,
                },
              },
            }),
          },
        ],
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("reject on error enabled", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory({
        errorOutputId: "af589f73-effe-4a80-b48f-fb912ac6ce67",
      }).build();

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

  describe("skip authorization type input id field if undefined", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory({ authorizationTypeInput: null }).build();

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
  });

  describe("skip bearer token if secret not found", () => {
    it("getNodeFile", async () => {
      vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockImplementation(
        // @ts-ignore
        async (idOrName) => {
          throw new VellumError({
            message: `Workspace secret '${idOrName}' not found`,
            statusCode: 404,
          });
        }
      );
      const nodeData = apiNodeFactory({
        bearerToken: nodeInputFactory({
          key: "bearer_token_value",
          value: {
            type: "WORKSPACE_SECRET",
            data: {
              type: "STRING",
              workspaceSecretId: "some-non-existent-workspace-secret-id",
            },
          },
        }),
      }).build();

      const workflowContext = workflowContextFactory({ strict: false });
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(workflowContext.getErrors()).toHaveLength(1);
      const error = workflowContext.getErrors()[0];
      expect(error).toBeInstanceOf(EntityNotFoundError);
      expect(error?.message).toContain(
        'Workspace Secret for attribute "bearer_token_value" not found.'
      );
      expect(error?.severity).toBe("WARNING");
    });
  });

  describe("api node with timeout", () => {
    it("should generate timeout field when timeout attribute is present", async () => {
      const nodeData = apiNodeFactory({
        attributes: [
          {
            id: "timeout-attr-id",
            name: "timeout",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "NUMBER", value: 30 },
            },
          },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should not generate timeout field when timeout attribute is not present", async () => {
      const nodeData = apiNodeFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should not generate timeout field when timeout attribute is null", async () => {
      const nodeData = apiNodeFactory({
        attributes: [
          {
            id: "timeout-attr-id",
            name: "timeout",
            value: null,
          },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("display class with base defaults", () => {
    it("should skip Display class when icon and color match base class defaults", async () => {
      const nodeData = apiNodeFactory({
        displayData: {
          icon: "vellum:icon:signal-stream",
          color: "lightBlue",
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
