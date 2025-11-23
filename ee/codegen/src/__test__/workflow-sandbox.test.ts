import { VellumVariable } from "vellum-ai/api";
import { StringInput } from "vellum-ai/api/types";

import { workflowContextFactory } from "./helpers";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";
import { nodeContextFactory } from "./helpers/node-context-factory";
import { genericNodeFactory } from "./helpers/node-data-factories";

import * as codegen from "src/codegen";
import { Writer } from "src/generators/extensions/writer";
import {
  WorkflowSandboxDatasetRow,
  WorkflowTrigger,
  WorkflowTriggerType,
} from "src/types/vellum";

describe("Workflow Sandbox", () => {
  const generateSandboxFile = async (
    inputVariables: VellumVariable[],
    generateSandboxInput: boolean = true
  ): Promise<string> => {
    const writer = new Writer();
    const uniqueWorkflowContext = workflowContextFactory();

    inputVariables.forEach((inputVariableData) => {
      uniqueWorkflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: inputVariableData,
          workflowContext: uniqueWorkflowContext,
        })
      );
    });

    const sandboxInputs: WorkflowSandboxDatasetRow[] = inputVariables.map(
      (inputVariableData) => {
        return generateSandboxInput
          ? [
              {
                name: inputVariableData.key,
                type: "STRING",
                value: "some-value",
              },
            ]
          : ([
              {
                name: inputVariableData.key,
                type: "STRING",
              },
            ] as StringInput[]);
      }
    );

    const sandbox = codegen.workflowSandboxFile({
      workflowContext: uniqueWorkflowContext,
      sandboxInputs,
    });

    sandbox.write(writer);
    return await writer.toStringFormatted();
  };

  describe("write", () => {
    it("should generate correct code given inputs", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "1", key: "some_foo", type: "STRING" },
        { id: "2", key: "some_bar", type: "STRING" },
      ];

      const sandboxFile = await generateSandboxFile(inputVariables);
      expect(sandboxFile).toMatchSnapshot();
    });

    it("should generate correct code for snake case input names", async () => {
      const snakeCasedVariables: VellumVariable[] = [
        { id: "1", key: "some_foo", type: "STRING" },
        { id: "2", key: "some_bar", type: "STRING" },
      ];

      const snakeCasedResult = await generateSandboxFile(snakeCasedVariables);
      expect(snakeCasedResult).toMatchSnapshot();
    });

    it("should generate correct code for camel case input names", async () => {
      const camelCasedVariables: VellumVariable[] = [
        { id: "1", key: "someFoo", type: "STRING" },
        { id: "2", key: "someBar", type: "STRING" },
      ];

      const camelCasedResult = await generateSandboxFile(camelCasedVariables);
      expect(camelCasedResult).toMatchSnapshot();
    });

    it("should generate correct code given optional input with default of null string value", async () => {
      const inputVariables: VellumVariable[] = [
        {
          id: "1",
          key: "some_foo",
          type: "STRING",
          required: false,
          default: { type: "STRING" },
        },
      ];

      const sandboxFile = await generateSandboxFile(inputVariables, false);
      expect(sandboxFile).toMatchSnapshot();
    });

    it("should properly handle special characters with escaped quotes", async () => {
      const writer = new Writer();
      const uniqueWorkflowContext = workflowContextFactory();
      const inputVariable: VellumVariable = {
        id: "1",
        key: "special_characters_input",
        type: "STRING",
      };

      uniqueWorkflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: inputVariable,
          workflowContext: uniqueWorkflowContext,
        })
      );

      // Create sandbox input with a URL containing quotes that would normally be escaped
      const sandboxInputs: WorkflowSandboxDatasetRow[] = [
        [
          {
            name: inputVariable.key,
            type: "STRING",
            value: '\\"special characters\\"',
          },
        ],
      ];

      const sandbox = codegen.workflowSandboxFile({
        workflowContext: uniqueWorkflowContext,
        sandboxInputs,
      });

      sandbox.write(writer);
      const result = await writer.toStringFormatted();
      expect(result).toMatchSnapshot();
    });

    it("should generate DatasetRow without inputs parameter when dataset row has label but no inputs", async () => {
      /**
       * Tests that dataset rows with labels but no inputs generate DatasetRow(label="...") without inputs parameter.
       */

      const writer = new Writer();
      const uniqueWorkflowContext = workflowContextFactory();
      const inputVariable: VellumVariable = {
        id: "1",
        key: "test_input",
        type: "STRING",
      };

      uniqueWorkflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: inputVariable,
          workflowContext: uniqueWorkflowContext,
        })
      );

      const sandboxInputs: WorkflowSandboxDatasetRow[] = [
        { label: "Test Label Only" },
      ];

      const sandbox = codegen.workflowSandboxFile({
        workflowContext: uniqueWorkflowContext,
        sandboxInputs,
      });

      sandbox.write(writer);
      const result = await writer.toStringFormatted();

      expect(result).toMatchSnapshot();
      expect(result).toContain('DatasetRow(label="Test Label Only")');
      expect(result).not.toContain("inputs=");
    });

    it("should generate DatasetRow with trigger when workflow_trigger_id is provided", async () => {
      const writer = new Writer();
      const triggerId = "550e8400-e29b-41d4-a716-446655440000";
      const triggers: WorkflowTrigger[] = [
        {
          id: triggerId,
          type: WorkflowTriggerType.SCHEDULED,
          attributes: [],
          cron: "* * * * *",
          timezone: "UTC",
        },
      ];
      const uniqueWorkflowContext = workflowContextFactory({ triggers });
      const inputVariable: VellumVariable = {
        id: "1",
        key: "test_input",
        type: "STRING",
      };

      uniqueWorkflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: inputVariable,
          workflowContext: uniqueWorkflowContext,
        })
      );

      const sandboxInputs: WorkflowSandboxDatasetRow[] = [
        {
          label: "Scenario with Trigger ID",
          inputs: [
            {
              name: inputVariable.key,
              type: "STRING",
              value: "test-value",
            },
          ],
          workflow_trigger_id: triggerId,
        },
        {
          label: "Scenario without Trigger ID",
          inputs: [
            {
              name: inputVariable.key,
              type: "STRING",
              value: "test-value-2",
            },
          ],
        },
      ];

      const sandbox = codegen.workflowSandboxFile({
        workflowContext: uniqueWorkflowContext,
        sandboxInputs,
      });

      sandbox.write(writer);
      const result = await writer.toStringFormatted();

      expect(result).toMatchSnapshot();
      expect(result).toContain("trigger=ScheduleTrigger");
      const lines = result.split("\n");
      const secondDatasetRowIndex = lines.findIndex((line) =>
        line.includes('label="Scenario without Trigger ID"')
      );
      expect(secondDatasetRowIndex).toBeGreaterThan(-1);
      const secondDatasetRowLine = lines[secondDatasetRowIndex];
      expect(secondDatasetRowLine).not.toContain("trigger=");
    });

    it("should generate DatasetRow with mocks when mocks are provided", async () => {
      const writer = new Writer();
      const uniqueWorkflowContext = workflowContextFactory();
      const inputVariable: VellumVariable = {
        id: "1",
        key: "test_input",
        type: "STRING",
      };

      uniqueWorkflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: inputVariable,
          workflowContext: uniqueWorkflowContext,
        })
      );

      const genericNodeData = genericNodeFactory();
      await nodeContextFactory({
        workflowContext: uniqueWorkflowContext,
        nodeData: genericNodeData,
      });

      const sandboxInputs: WorkflowSandboxDatasetRow[] = [
        {
          label: "Scenario with Mocks",
          inputs: [
            {
              name: inputVariable.key,
              type: "STRING",
              value: "test-value",
            },
          ],
          mocks: [
            {
              node_id: genericNodeData.id,
              when_condition: {
                type: "BINARY_EXPRESSION",
                operator: "=",
                lhs: {
                  type: "WORKFLOW_INPUT",
                  inputVariableId: "1",
                },
                rhs: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "STRING",
                    value: "test-value",
                  },
                },
              },
              then_outputs: {
                result: "mocked_result",
                count: 42,
                flag: true,
                payload: { foo: "bar", nested: { value: 123 } },
              },
            },
          ],
        },
        {
          label: "Scenario without Mocks",
          inputs: [
            {
              name: inputVariable.key,
              type: "STRING",
              value: "test-value-2",
            },
          ],
        },
      ];

      const sandbox = codegen.workflowSandboxFile({
        workflowContext: uniqueWorkflowContext,
        sandboxInputs,
      });

      sandbox.write(writer);
      const result = await writer.toStringFormatted();

      expect(result).toMatchSnapshot();
    });
  });
});
