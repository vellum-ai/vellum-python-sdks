import { Writer } from "@fern-api/python-ast/core/Writer";
import { Vellum } from "vellum-ai";
import { VellumVariable } from "vellum-ai/api";
import { VellumVariableType } from "vellum-ai/api/types";

import { workflowContextFactory } from "./helpers";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";

describe("Inputs", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("write", () => {
    it("should generate correct code when Inputs has no variables", async () => {
      const inputs = codegen.inputs({ workflowContext });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when Inputs has variables", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "input1", key: "input1", type: "STRING", required: true },
        { id: "input2", key: "input2", type: "NUMBER", required: true },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({ workflowContext });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when Inputs has variables with empty keys", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "input1", key: "", type: "STRING", required: true },
        { id: "input2", key: "", type: "STRING", required: true },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({ workflowContext });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when Inputs has variables with duplicate keys", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "input1", key: "key-1", type: "STRING", required: true },
        { id: "input2", key: "key-1", type: "STRING", required: true },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({ workflowContext });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when Inputs has a custom name", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "input1", key: "input1", type: "STRING", required: true },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({
        workflowContext,
        name: "CustomInputs",
      });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should not generate any code when Inputs is empty", async () => {
      const inputs = codegen.inputs({ workflowContext });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toBe("");
    });

    it("should generate correct code for complex input variables", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "1", key: "query", type: "STRING", required: true },
        { id: "2", key: "max_runtime", type: "NUMBER", required: true },
        {
          id: "3",
          key: "previous_chat_history",
          type: "CHAT_HISTORY",
          required: true,
        },
        {
          id: "4",
          key: "prior_results",
          type: "SEARCH_RESULTS",
          required: true,
        },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({
        workflowContext,
      });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should convert input variable names into valid python attributes", async () => {
      const inputVariables: VellumVariable[] = [
        { id: "1", key: "My Input", type: "STRING", required: true },
        { id: "2", key: "$My*Input", type: "NUMBER", required: true },
        { id: "4", key: "123", type: "STRING", required: true },
        { id: "3", key: "_a", type: "STRING", required: true },
        { id: "5", key: "_123", type: "STRING", required: true },
      ];
      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });
      const inputs = codegen.inputs({
        workflowContext,
      });

      inputs.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it.each([
      {
        type: VellumVariableType.String,
        key: "string_input",
        default: {
          type: "STRING",
          value: "Example String",
        } as Vellum.StringVellumValue,
      },
      {
        type: VellumVariableType.Number,
        key: "number_input",
        default: { type: "NUMBER", value: 123 } as Vellum.NumberVellumValue,
      },
      {
        type: VellumVariableType.Json,
        key: "json_input",
        default: {
          type: "JSON",
          value: { key: "value" },
        } as Vellum.JsonVellumValue,
      },
      {
        type: VellumVariableType.Image,
        key: "image_input",
        value: {
          type: "IMAGE",
          default: {
            src: "IMAGE",
          } as Vellum.VellumImage,
        } as Vellum.ImageVellumValue,
      },
      {
        type: VellumVariableType.Audio,
        key: "audio_input",
        value: {
          type: "AUDIO",
          default: {
            src: "AUDIO",
          } as Vellum.VellumAudio,
        } as Vellum.AudioVellumValue,
      },
      {
        type: VellumVariableType.FunctionCall,
        key: "function_call_input",
        default: {
          type: "FUNCTION_CALL",
          value: {
            arguments: { arg1: "Hello World" },
            name: "function_call",
          } as Vellum.FunctionCall,
        } as Vellum.FunctionCallVellumValue,
      },
      {
        type: VellumVariableType.Error,
        key: "error_input",
        default: {
          type: "ERROR",
          value: {
            message: "Some 500 error",
            code: Vellum.VellumErrorCodeEnum.InternalServerError,
          } as Vellum.VellumError,
        } as Vellum.ErrorVellumValue,
      },
      {
        type: VellumVariableType.Array,
        key: "array_input",
        default: {
          type: "ARRAY",
          value: [
            {
              type: "STRING",
              value: "Example String",
            } as Vellum.StringVellumValue,
            { type: "NUMBER", value: 123 } as Vellum.NumberVellumValue,
          ],
        } as Vellum.ArrayVellumValue,
      },
      {
        type: VellumVariableType.ChatHistory,
        key: "chat_history_input",
        default: {
          type: "CHAT_HISTORY",
          value: [
            {
              text: "foo bar",
              role: Vellum.ChatMessageRole.User,
            } as Vellum.ChatMessage,
          ],
        } as Vellum.ChatHistoryVellumValue,
      },
      {
        type: VellumVariableType.SearchResults,
        key: "search_results_input",
        default: {
          type: "SEARCH_RESULTS",
          value: [
            {
              text: "Hello, World!",
              score: 1.0,
              keywords: ["foo", "bar"],
              document: {
                label: "Example Document",
              } as Vellum.SearchResultDocument,
            } as Vellum.SearchResult,
          ],
        } as Vellum.SearchResultsVellumValue,
      },
      {
        type: VellumVariableType.Json,
        key: "json_array_input",
        default: {
          type: "JSON",
          value: [],
        } as Vellum.JsonVellumValue,
      },
    ])(
      "should generate correct code when default is a $type",
      async ({ type, key, default: defaultValue }) => {
        const extensions: Vellum.VellumVariableExtensions = {
          color: "red",
        };
        const inputVariables: VellumVariable[] = [
          {
            id: "some-id",
            key,
            type,
            required: true,
            default: defaultValue,
            extensions: extensions,
          },
        ];

        inputVariables.forEach((inputVariableData) => {
          workflowContext.addInputVariableContext(
            inputVariableContextFactory({
              inputVariableData,
              workflowContext,
            })
          );
        });

        const inputs = codegen.inputs({ workflowContext });

        inputs.write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );

    it("should generate correct Optional types when required is false", async () => {
      const inputVariables: VellumVariable[] = [
        {
          id: "1",
          key: "foo",
          type: "STRING",
          default: { type: "STRING", value: "Example String" },
          required: false,
        },
        {
          id: "2",
          key: "bar",
          type: "NUMBER",
          default: { type: "NUMBER", value: 123 },
          required: false,
        },
      ];

      inputVariables.forEach((inputVariableData) => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: inputVariableData,
            workflowContext,
          })
        );
      });

      const inputs = codegen.inputs({ workflowContext });
      inputs.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
