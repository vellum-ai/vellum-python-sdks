import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { NodeOutput as NodeOutputType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

export declare namespace NodeOutputs {
  export interface Args {
    nodeOutputs: NodeOutputType[];
    nodeContext: GenericNodeContext;
    workflowContext: WorkflowContext;
  }
}

export class NodeOutputs extends AstNode {
  private astNode: AstNode;

  public constructor(args: NodeOutputs.Args) {
    super();

    this.astNode = this.constructNodeOutputs(
      args.nodeOutputs,
      args.nodeContext,
      args.workflowContext
    );
  }

  private constructNodeOutputs(
    nodeOutputs: NodeOutputType[],
    nodeContext: GenericNodeContext,
    workflowContext: WorkflowContext
  ): AstNode {
    const baseNodeClassNameAlias =
      nodeContext.baseNodeClassName === nodeContext.nodeClassName
        ? `Base${nodeContext.baseNodeClassName}`
        : undefined;

    const clazz = python.class_({
      name: "Outputs",
      extends_: [
        python.reference({
          name: nodeContext.baseNodeClassName,
          modulePath: nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
          attribute: ["Outputs"],
        }),
      ],
    });

    nodeOutputs.forEach((output) => {
      const type = getVellumVariablePrimitiveType(output.type);
      const field = output.value
        ? python.field({
            name: output.name,
            initializer: new WorkflowValueDescriptor({
              workflowValueDescriptor: output.value,
              workflowContext: workflowContext,
            }),
          })
        : python.field({
            name: output.name,
            type: type,
          });
      clazz.addField(field);
    });

    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
