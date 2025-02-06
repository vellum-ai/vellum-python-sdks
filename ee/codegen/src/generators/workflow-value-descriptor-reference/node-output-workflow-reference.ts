import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { NodeOutputWorkflowReference as NodeOutputWorkflowReferenceType } from "src/types/vellum";

export class NodeOutputWorkflowReference extends BaseNodeInputWorkflowReference<NodeOutputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const nodeOutputPointer = this.nodeInputWorkflowReferencePointer;

    const nodeContext = this.workflowContext.getNodeContext(
      nodeOutputPointer.nodeId
    );

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
      return python.reference({
        name: nodeContext.nodeClassName,
        modulePath: nodeContext.nodeModulePath,
        attribute: [OUTPUTS_CLASS_NAME, nodeOutputName],
      });
    }
    return undefined;
  }
}
