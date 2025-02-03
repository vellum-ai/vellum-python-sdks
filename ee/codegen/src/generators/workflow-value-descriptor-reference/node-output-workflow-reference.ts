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
      return python.reference({
        name: nodeContext.nodeClassName,
        modulePath: nodeContext.nodeModulePath,
        attribute: [OUTPUTS_CLASS_NAME, nodeOutputName],
      });
    }
    return undefined;
  }
}
