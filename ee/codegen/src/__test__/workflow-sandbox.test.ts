import { Writer } from "@fern-api/python-ast/core/Writer";
import { VellumVariable } from "vellum-ai/api";
import { StringInput } from "vellum-ai/api/types";

import { workflowContextFactory } from "./helpers";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";

import * as codegen from "src/codegen";
import { WorkflowSandboxInputs } from "src/types/vellum";

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

    const sandboxInputs: WorkflowSandboxInputs[] = inputVariables.map(
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

    it("should generate correct and same code for snake and camel casing of input names", async () => {
      const snakeCasedVariables: VellumVariable[] = [
        { id: "1", key: "some_foo", type: "STRING" },
        { id: "2", key: "some_bar", type: "STRING" },
      ];

      const camelCasedVariables: VellumVariable[] = [
        { id: "1", key: "someFoo", type: "STRING" },
        { id: "2", key: "someBar", type: "STRING" },
      ];

      const snakeCasedResult = await generateSandboxFile(snakeCasedVariables);
      const camelCasedResult = await generateSandboxFile(camelCasedVariables);

      // Assert that both results match the same snapshot
      expect(snakeCasedResult).toEqual(camelCasedResult);
      expect(snakeCasedResult).toMatchSnapshot();
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
      const sandboxInputs: WorkflowSandboxInputs[] = [
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
  });
});
