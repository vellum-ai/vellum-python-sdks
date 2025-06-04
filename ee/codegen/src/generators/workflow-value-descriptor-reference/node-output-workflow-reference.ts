import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { NodeOutputWorkflowReference as NodeOutputWorkflowReferenceType } from "src/types/vellum";

export class NodeOutputWorkflowReference extends BaseNodeInputWorkflowReference<NodeOutputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const nodeOutputPointer = this.nodeInputWorkflowReferencePointer;

    const nodeContext = this.workflowContext.findNodeContext(
      nodeOutputPointer.nodeId
    );

    if (!nodeContext) {
      return python.TypeInstantiation.none();
    }

    const nodeOutputName = nodeContext.getNodeOutputNameById(
      nodeOutputPointer.nodeOutputId
    );

    if (nodeOutputName) {
      if (this.nodeContext && this.nodeContext.isImportedBefore(nodeContext)) {
        return python.instantiateClass({
          classReference: python.reference({
            name: "LazyReference",
            modulePath: [
              ...this.nodeContext.workflowContext.sdkModulePathNames
                .WORKFLOWS_MODULE_PATH,
              "references",
            ],
          }),
          arguments_: [
            python.methodArgument({
              value: python.TypeInstantiation.str(
                `${nodeContext.nodeClassName}.${OUTPUTS_CLASS_NAME}.${nodeOutputName}`
              ),
            }),
          ],
        });
      }
      if (this.nodeContext?.nodeClassName === nodeContext.nodeClassName) {
        return python.instantiateClass({
          classReference: python.reference({
            name: "LazyReference",
            modulePath: [
              ...this.nodeContext.workflowContext.sdkModulePathNames
                .WORKFLOWS_MODULE_PATH,
              "references",
            ],
          }),
          arguments_: [
            python.methodArgument({
              value: python.lambda({
                body: python.accessAttribute({
                  lhs: python.reference({
                    name: nodeContext.nodeClassName,
                    modulePath: [],
                  }),
                  rhs: python.reference({
                    name: `${OUTPUTS_CLASS_NAME}.${nodeOutputName}`,
                    modulePath: [],
                  }),
                }),
              }),
            }),
          ],
        });
      } else {
        return python.reference({
          name: nodeContext.nodeClassName,
          modulePath: nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, nodeOutputName],
        });
      }
    }
    return python.TypeInstantiation.none();
  }
}
