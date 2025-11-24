import { NodeInputValuePointer } from "./node-input-value-pointer";

import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";
import { NodeInput as NodeInputType, WorkflowDataNode } from "src/types/vellum";

export declare namespace NodeInput {
  export interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputData: NodeInputType;
  }
}

export class NodeInput extends AstNode {
  private nodeContext: BaseNodeContext<WorkflowDataNode>;
  public nodeInputData: NodeInputType;
  public nodeInputValuePointer: NodeInputValuePointer;

  public constructor(args: NodeInput.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.nodeInputData = args.nodeInputData;

    this.nodeInputValuePointer = this.generateNodeInputValuePointer();
  }

  private generateNodeInputValuePointer(): NodeInputValuePointer {
    const nodeInputValuePointer = new NodeInputValuePointer({
      nodeContext: this.nodeContext,
      nodeInputValuePointerData: this.nodeInputData.value,
    });
    this.inheritReferences(nodeInputValuePointer);
    return nodeInputValuePointer;
  }

  write(writer: Writer): void {
    this.nodeInputValuePointer.write(writer);
  }
}
