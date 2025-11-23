import { nodeContextFactory } from "src/__test__/helpers";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { ConstantValuePointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/constant-value-pointer";
import { ConstantValuePointer, WorkflowDataNode } from "src/types/vellum";

describe("ConstantValuePointer", () => {
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    nodeContext = await nodeContextFactory();
  });

  it("should generate correct AST for STRING constant value", async () => {
    const constantValuePointer: ConstantValuePointer = {
      type: "CONSTANT_VALUE",
      data: {
        type: "STRING",
        value: "Hello, World!",
      },
    };

    const rule = new ConstantValuePointerRule({
      nodeContext,
      nodeInputValuePointerRule: constantValuePointer,
    });

    const writer = new Writer();
    rule.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
