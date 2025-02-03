import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { NodeInputValuePointer } from "./node-input-value-pointer";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInput as NodeInputType, WorkflowDataNode } from "src/types/vellum";

export declare namespace NodeInput {
  export interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    workflowContext: WorkflowContext;
    nodeInputData: NodeInputType;
  }
}

export class NodeInput extends AstNode {
  private nodeContext: BaseNodeContext<WorkflowDataNode>;
  private workflowContext: WorkflowContext;
  public nodeInputData: NodeInputType;
  public nodeInputValuePointer: NodeInputValuePointer;

  public constructor(args: NodeInput.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.nodeInputData = args.nodeInputData;

    this.nodeInputValuePointer = this.generateNodeInputValuePointer();
  }

  private generateNodeInputValuePointer(): NodeInputValuePointer {
    const nodeInputValuePointer = new NodeInputValuePointer({
      workflowContext: this.workflowContext,
      nodeInputValuePointerData: this.nodeInputData.value,
    });
    this.inheritReferences(nodeInputValuePointer);
    return nodeInputValuePointer;
  }

  write(writer: Writer): void {
    this.nodeInputValuePointer.write(writer);
  }
}
