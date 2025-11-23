import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { Writer } from "src/generators/extensions/writer";
import { WorkflowStatePointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/workflow-state-pointer";

describe("WorkflowStatePointer", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code", async () => {
    const workflowContext = workflowContextFactory();
    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        stateVariableData: {
          id: "test-state-id",
          key: "state_1",
          type: "STRING",
          default: null,
          required: false,
          extensions: { color: "cyan" },
        },
        workflowContext,
      })
    );

    const nodeContext = await nodeContextFactory({ workflowContext });

    const workflowStatePointer = new WorkflowStatePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "WORKFLOW_STATE",
        data: {
          stateVariableId: "test-state-id",
        },
      },
    });

    workflowStatePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle when it's referencing a state variable that no longer exists", async () => {
    const workflowContext = workflowContextFactory({ strict: false });
    const nodeContext = await nodeContextFactory({ workflowContext });

    const workflowStatePointer = new WorkflowStatePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "WORKFLOW_STATE",
        data: {
          stateVariableId: "missing-state-id",
        },
      },
    });

    workflowStatePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
