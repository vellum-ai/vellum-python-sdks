import { Writer } from "@fern-api/python-ast/core/Writer";
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
import { ApiNode } from "src/generators/nodes/api-node";
import { ApiNode as ApiNodeType, NodeInput } from "src/types/vellum";

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

  describe("basic api node", () => {
    it("should handle missing url field gracefully", async () => {
      // GIVEN a node without a url field
      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "GET",
                },
              },
            ],
            combinator: "OR",
          },
        },
        // url input is missing
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [],
            combinator: "OR",
          },
        },
      ];

      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
        },
        inputs: inputs,
      };

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
    it("should only generate url field", async () => {
      // GIVEN a node with only url and GET method
      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "GET",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [],
            combinator: "OR",
          },
        },
      ];
      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
        },
        inputs: inputs,
      };
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should only contain the url field
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("should generate method field when method is POST", async () => {
      // GIVEN a node with url and POST method
      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "POST",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [],
            combinator: "OR",
          },
        },
      ];
      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
        },
        inputs: inputs,
      };
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should contain both url and method fields
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("should not generate body field when body is empty", async () => {
      // GIVEN a node with url, GET method, and body
      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "GET",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "JSON",
                  value: {},
                },
              },
            ],
            combinator: "OR",
          },
        },
      ];
      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
        },
        inputs: inputs,
      };
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should contain url and json fields
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate headers field when headers are provided", async () => {
      // GIVEN a node with url, GET method, and headers
      const headerKeyInputId = "header-key-input-id";
      const headerValueInputId = "header-value-input-id";

      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "GET",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [],
            combinator: "OR",
          },
        },
        {
          id: headerKeyInputId,
          key: "header-key",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "Content-Type",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: headerValueInputId,
          key: "header-value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "application/json",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ];

      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
          additionalHeaders: [
            {
              headerKeyInputId: headerKeyInputId,
              headerValueInputId: headerValueInputId,
            },
          ],
        },
        inputs: inputs,
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should contain url and headers fields
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate API key header fields when API key is provided", async () => {
      // GIVEN a node with url, GET method, and API key header
      const apiKeyHeaderKeyInputId = "api-key-header-key-input-id";
      const apiKeyHeaderValueInputId = "api-key-header-value-input-id";
      const authTypeInputId = "auth-type-input-id";

      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "GET",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [],
            combinator: "OR",
          },
        },
        {
          id: apiKeyHeaderKeyInputId,
          key: "api-key-header-key",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "X-API-KEY",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: apiKeyHeaderValueInputId,
          key: "api-key-header-value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "my-api-key",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: authTypeInputId,
          key: "authorization-type",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "API_KEY",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ];

      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
          apiKeyHeaderKeyInputId: apiKeyHeaderKeyInputId,
          apiKeyHeaderValueInputId: apiKeyHeaderValueInputId,
          authorizationTypeInputId: authTypeInputId,
        },
        inputs: inputs,
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should contain url and API key header fields
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate all fields when all conditions are provided", async () => {
      // GIVEN a node with all possible fields
      const headerKeyInputId = "header-key-input-id";
      const headerValueInputId = "header-value-input-id";
      const apiKeyHeaderKeyInputId = "api-key-header-key-input-id";
      const apiKeyHeaderValueInputId = "api-key-header-value-input-id";
      const authTypeInputId = "auth-type-input-id";

      const inputs: NodeInput[] = [
        {
          id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          key: "method",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "STRING" as const,
                  value: "POST",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "480a4c12-22d6-4223-a38a-85db5eda118c",
          key: "url",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "https://example.vellum.ai",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          key: "body",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "JSON",
                  value: { foo: "bar" },
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: headerKeyInputId,
          key: "header-key",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "Content-Type",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: headerValueInputId,
          key: "header-value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "application/json",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: apiKeyHeaderKeyInputId,
          key: "api-key-header-key",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "X-API-KEY",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: apiKeyHeaderValueInputId,
          key: "api-key-header-value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "my-api-key",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: authTypeInputId,
          key: "authorization-type",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "API_KEY",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ];

      const nodeData: ApiNodeType = {
        id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
        type: "API",
        data: {
          label: "API Node",
          methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
          urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
          bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
          textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
          jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
          statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
          targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
          sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
          additionalHeaders: [
            {
              headerKeyInputId: headerKeyInputId,
              headerValueInputId: headerValueInputId,
            },
          ],
          apiKeyHeaderKeyInputId: apiKeyHeaderKeyInputId,
          apiKeyHeaderValueInputId: apiKeyHeaderValueInputId,
          authorizationTypeInputId: authTypeInputId,
        },
        inputs: inputs,
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ApiNodeContext;

      const node = new ApiNode({
        workflowContext,
        nodeContext,
      });

      // WHEN generating the code
      node.getNodeFile().write(writer);

      // THEN the generated code should contain all fields
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

  describe("skip authorization type input id field if undefined", () => {
    beforeEach(async () => {
      const nodeData = apiNodeFactory({ authorizationTypeInput: null });

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
      });

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
});
