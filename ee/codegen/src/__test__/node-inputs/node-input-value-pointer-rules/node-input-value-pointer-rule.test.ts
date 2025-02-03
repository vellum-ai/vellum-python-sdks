import { Writer } from "@fern-api/python-ast/core/Writer";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInputValuePointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/node-input-value-pointer-rule";
import {
  NodeInputValuePointerRule as NodeInputValuePointerRuleType,
  WorkflowDataNode,
} from "src/types/vellum";

describe("NodeInputValuePointerRule", () => {
  let writer: Writer;
  let workflowContext: WorkflowContext;
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    writer = new Writer();
    workflowContext = workflowContextFactory();
    nodeContext = await nodeContextFactory({ workflowContext });
  });

  it("should generate correct AST for CONSTANT_VALUE pointer", async () => {
    const constantValuePointer: NodeInputValuePointerRuleType = {
      type: "CONSTANT_VALUE",
      data: {
        type: "STRING",
        value: "Hello, World!",
      },
    };

    const rule = new NodeInputValuePointerRule({
      nodeContext,
      nodeInputValuePointerRuleData: constantValuePointer,
    });

    rule.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for NODE_OUTPUT pointer", async () => {
    vi.spyOn(nodeContext.workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeOutputPointer: NodeInputValuePointerRuleType = {
      type: "NODE_OUTPUT",
      data: {
        nodeId: "test-node-id",
        outputId: "test-output-id",
      },
    };

    const rule = new NodeInputValuePointerRule({
      nodeContext,
      nodeInputValuePointerRuleData: nodeOutputPointer,
    });

    rule.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for INPUT_VARIABLE pointer", async () => {
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

    const inputVariablePointer: NodeInputValuePointerRuleType = {
      type: "INPUT_VARIABLE",
      data: {
        inputVariableId: "test-input-id",
      },
    };

    const rule = new NodeInputValuePointerRule({
      nodeContext,
      nodeInputValuePointerRuleData: inputVariablePointer,
    });

    rule.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
