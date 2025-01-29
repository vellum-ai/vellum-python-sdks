import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { NodeInputValuePointer } from "./node-input-value-pointer";

import { WorkflowContext } from "src/context";
import { NodeInput as NodeInputType } from "src/types/vellum";

export declare namespace NodeInput {
  export interface Args {
    workflowContext: WorkflowContext;
    nodeInputData: NodeInputType;
  }
}

export class NodeInput extends AstNode {
  private workflowContext: WorkflowContext;
  nodeInputData: NodeInputType;
  public nodeInputValuePointer: NodeInputValuePointer;

  public constructor(args: NodeInput.Args) {
    super();

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
