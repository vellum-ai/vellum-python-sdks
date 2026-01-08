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

  describe("write", () => {
    it("should generate correct code when State has no variables", async () => {
      const state = codegen.state({ workflowContext });

      state.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when State has variables", async () => {
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "variable1",
            key: "variable1",
            type: "STRING",
            required: true,
          },
          workflowContext,
        })
      );
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: "variable2",
            key: "variable2",
            type: "NUMBER",
            required: true,
          },
          workflowContext,
        })
      );

      const state = codegen.state({ workflowContext });

      state.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when State has a custom name", async () => {
      const stateVariableContext = stateVariableContextFactory({
        stateVariableData: {
          id: "variable1",
          key: "variable1",
          type: "STRING",
          required: true,
        },
        workflowContext,
      });
      // Override the definition name to test custom state class names
      (stateVariableContext.definition as { name: string }).name =
        "CustomState";
      workflowContext.addStateVariableContext(stateVariableContext);

      const state = codegen.state({ workflowContext });

      state.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
