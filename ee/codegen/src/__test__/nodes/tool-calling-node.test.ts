import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  nodePortFactory,
  toolCallingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import {
  DeploymentWorkflowFunctionArgs,
  FunctionArgs,
  NodeAttribute,
  NodePort,
} from "src/types/vellum";

describe("ToolCallingNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "location",
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
          id: "2544f9e4-d6e6-4475-b6a9-13393115d77c",
        }),
      ];
      const nodeData = toolCallingNodeFactory({ nodePorts: nodePortData });

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

  describe("input variables", () => {
    it("should generate input variables", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [
          {
            id: "b5ae358b-e111-4209-9a3e-4e7126f2d391",
            name: "ml_model",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "gpt-4o-mini" },
            },
          },
          {
            id: "be73bec8-a35a-43b1-b140-9541ba837f8e",
            name: "prompt_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  id: "1dc7d5dc-c41d-4a9b-8add-1e0c6705da04",
                  key: "text",
                  value: null,
                },
              ],
            },
          },
          {
            id: "dfdafe9a-1dae-4895-8a08-22b71c0119ff",
            name: "blocks",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    blocks: [
                      {
                        blocks: [
                          {
                            text: "Summarize the following text:\n\n",
                            block_type: "PLAIN_TEXT",
                          },
                          {
                            block_type: "VARIABLE",
                            input_variable:
                              "1dc7d5dc-c41d-4a9b-8add-1e0c6705da04",
                          },
                        ],
                        block_type: "RICH_TEXT",
                      },
                    ],
                    chat_role: "SYSTEM",
                    block_type: "CHAT_MESSAGE",
                  },
                ],
              },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("function ordering", () => {
    const createFunctionAttribute = <T>(
      functions: Array<T>
    ): NodeAttribute => ({
      id: "functions-attr-id",
      name: "functions",
      value: {
        type: "CONSTANT_VALUE",
        value: {
          type: "JSON",
          value: functions,
        },
      },
    });

    const codeExecutionFunction: FunctionArgs = {
      type: "CODE_EXECUTION",
      src: 'def add_numbers(a: int, b: int) -> int:\n    """\n    Add two numbers together.\n    """\n    return a + b\n',
      name: "add_numbers",
      description: "Add two numbers together.",
      definition: {
        name: "add_numbers",
        parameters: {
          type: "object",
          required: ["a", "b"],
          properties: {
            a: { type: "integer" },
            b: { type: "integer" },
          },
        },
      },
    };

    const inlineWorkflowFunction = {
      type: "INLINE_WORKFLOW",
      exec_config: {
        workflow_raw_data: {
          nodes: [
            {
              id: "entrypoint",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint Node",
                source_handle_id: "entry-source",
              },
              inputs: [],
            },
            {
              id: "subtract-node",
              type: "GENERIC",
              label: "SubtractNode",
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              attributes: [],
              outputs: [
                {
                  id: "subtract-output",
                  name: "result",
                  type: "NUMBER",
                },
              ],
              ports: [],
              trigger: {
                id: "subtract-trigger",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
            },
          ],
          edges: [
            {
              id: "edge-1",
              type: "DEFAULT",
              source_node_id: "entrypoint",
              source_handle_id: "entry-source",
              target_node_id: "subtract-node",
              target_handle_id: "subtract-trigger",
            },
          ],
          definition: {
            name: "SubtractWorkflow",
            module: ["workflows", "subtract"],
          },
        },
        input_variables: [
          {
            id: "input-a",
            key: "a",
            type: "NUMBER",
            default: null,
            required: true,
            extensions: { color: null },
          },
          {
            id: "input-b",
            key: "b",
            type: "NUMBER",
            default: null,
            required: true,
            extensions: { color: null },
          },
        ],
        output_variables: [
          {
            id: "output-result",
            key: "result",
            type: "NUMBER",
          },
        ],
      },
    };

    it("should preserve order: code-exec, workflow", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = createFunctionAttribute([
        codeExecutionFunction,
        inlineWorkflowFunction,
      ]);

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should preserve order: workflow, code-exec", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = createFunctionAttribute([
        inlineWorkflowFunction,
        codeExecutionFunction,
      ]);

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
  describe("deployment workflow", () => {
    const createFunctionAttribute = <T>(
      functions: Array<T>
    ): NodeAttribute => ({
      id: "functions-attr-id",
      name: "functions",
      value: {
        type: "CONSTANT_VALUE",
        value: {
          type: "JSON",
          value: functions,
        },
      },
    });

    const deploymentWorkflowFunction: DeploymentWorkflowFunctionArgs = {
      type: "WORKFLOW_DEPLOYMENT",
      name: "deployment_1",
      description: "Deployment 1 description",
      deployment: "deployment_1",
      release_tag: null,
    };

    it("should generate latest release tag if release_tag is null", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = createFunctionAttribute([
        deploymentWorkflowFunction,
      ]);

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
