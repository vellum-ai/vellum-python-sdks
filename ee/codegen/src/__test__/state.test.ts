import { Vellum } from "vellum-ai";

import { workflowContextFactory } from "./helpers";
import { stateVariableContextFactory } from "./helpers/state-variable-context-factory";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";

describe("State", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("chat history state default value handling", () => {
    it("should generate correct code for chat history state with empty list default", async () => {
      /**
       * Tests that a chat history state variable with an empty list default
       * generates Field(default_factory=list) to avoid mutable default issues.
       */

      // GIVEN a state variable with chat history type and empty list default
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "chat-history-state-id",
            key: "chat_history",
            type: "CHAT_HISTORY",
            required: false,
            default: { type: "CHAT_HISTORY", value: [] },
          },
          workflowContext,
        })
      );

      // WHEN we generate the state class
      const state = codegen.state({ workflowContext });
      state.write(writer);

      // THEN the generated code should use Field(default_factory=list)
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code for chat history state with non-empty list default", async () => {
      /**
       * Tests that a chat history state variable with a non-empty list default
       * generates Field(default_factory=lambda: [...]) to avoid mutable default issues.
       */

      // GIVEN a state variable with chat history type and non-empty list default
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "chat-history-state-id",
            key: "chat_history",
            type: "CHAT_HISTORY",
            required: false,
            default: {
              type: "CHAT_HISTORY",
              value: [
                {
                  text: "Hello, how can I help you?",
                  role: Vellum.ChatMessageRole.Assistant,
                } as Vellum.ChatMessage,
              ],
            },
          },
          workflowContext,
        })
      );

      // WHEN we generate the state class
      const state = codegen.state({ workflowContext });
      state.write(writer);

      // THEN the generated code should use Field(default_factory=lambda: [...])
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code for required chat history state with empty list default", async () => {
      /**
       * Tests that a required chat history state variable with an empty list default
       * generates Field(default_factory=list) without Optional type.
       */

      // GIVEN a required state variable with chat history type and empty list default
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "chat-history-state-id",
            key: "chat_history",
            type: "CHAT_HISTORY",
            required: true,
            default: { type: "CHAT_HISTORY", value: [] },
          },
          workflowContext,
        })
      );

      // WHEN we generate the state class
      const state = codegen.state({ workflowContext });
      state.write(writer);

      // THEN the generated code should use Field(default_factory=list) without Optional
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code for chat history state without default", async () => {
      /**
       * Tests that a chat history state variable without a default value
       * generates a simple type annotation without Field.
       */

      // GIVEN a state variable with chat history type and no default
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "chat-history-state-id",
            key: "chat_history",
            type: "CHAT_HISTORY",
            required: true,
          },
          workflowContext,
        })
      );

      // WHEN we generate the state class
      const state = codegen.state({ workflowContext });
      state.write(writer);

      // THEN the generated code should have a simple type annotation
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code for optional chat history state without default", async () => {
      /**
       * Tests that an optional chat history state variable without a default value
       * generates Optional type with None default.
       */

      // GIVEN an optional state variable with chat history type and no default
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "chat-history-state-id",
            key: "chat_history",
            type: "CHAT_HISTORY",
            required: false,
          },
          workflowContext,
        })
      );

      // WHEN we generate the state class
      const state = codegen.state({ workflowContext });
      state.write(writer);

      // THEN the generated code should have Optional type with None default
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
