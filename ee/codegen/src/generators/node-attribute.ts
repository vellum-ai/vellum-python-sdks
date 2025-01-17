import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeAttribute as NodeAttributeType } from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export declare namespace NodeAttributes {
  export interface Args {
    nodeAttributes: NodeAttributeType[];
    nodeContext: GenericNodeContext;
    workflowContext: WorkflowContext;
  }
}

export class NodeAttributes extends AstNode {
  private nodeContext: GenericNodeContext;
  private workflowContext: WorkflowContext;
  private astNode: AstNode | undefined = undefined;

  public constructor(args: NodeAttributes.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.astNode = this.constructNodeAttributes(args.nodeAttributes);
  }

  private constructNodeAttributes(
    nodeAttributes: NodeAttributeType[]
  ): AstNode | undefined {

    nodeAttributes.forEach((attribute) => {
      fields.push(
        python.field({
          name: attribute.name,
          initializer: attributeExpression,
        })
      );
    });

    fields.forEach((field) => clazz.add(field));

    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }

  private generateNodeAttributeExpression(nodeAttribute: NodeAttributeType) {
    return python.invokeMethod({
      methodReference: python.reference({
        name: "Attribute",
        modulePath:
          this.workflowContext.sdkModulePathNames.ATTRIBUTES_MODULE_PATH,
      }),
      arguments_: [
        python.methodArgument({
          value: this.buildDescriptor(nodeAttribute),
        }),
      ],
    });
  }

  private buildDescriptor(nodeAttribute: NodeAttributeType): AstNode {
    const expression = nodeAttribute.value;
    if (!expression) {
      return python.TypeInstantiation.none();
    }

    // TODO: Implement value descriptor conversion
    return python.TypeInstantiation.none();
  }
}
