import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { Writer } from "src/generators/extensions/writer";
import { InputVariablePointerRule } from "src/generators/node-inputs";

describe("InputVariablePointer", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code", async () => {
    const workflowContext = workflowContextFactory();
    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "test-input-id",
          key: "testVariable",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const nodeContext = await nodeContextFactory({ workflowContext });

    const inputVariablePointer = new InputVariablePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "INPUT_VARIABLE",
        data: {
          inputVariableId: "test-input-id",
        },
      },
    });

    inputVariablePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle when it's referencing an input variable that no longer exists", async () => {
    const workflowContext = workflowContextFactory({ strict: false });
    const nodeContext = await nodeContextFactory({ workflowContext });

    const inputVariablePointer = new InputVariablePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "INPUT_VARIABLE",
        data: {
          inputVariableId: "missing-input-id",
        },
      },
    });

    inputVariablePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
