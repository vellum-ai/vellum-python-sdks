import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeOutputPointer, WorkflowDataNode } from "src/types/vellum";

export class NodeOutputPointerRule extends BaseNodeInputValuePointerRule<NodeOutputPointer> {
  getReferencedNodeContext(): BaseNodeContext<WorkflowDataNode> {
    const nodeOutputPointerRuleData = this.nodeInputValuePointerRule.data;

    return this.workflowContext.getNodeContext(
      nodeOutputPointerRuleData.nodeId
    );
  }

  getAstNode(): python.Reference | undefined {
    const nodeOutputPointerRuleData = this.nodeInputValuePointerRule.data;

    const nodeContext = this.getReferencedNodeContext();

    const nodeOutputName = nodeContext.getNodeOutputNameById(
      nodeOutputPointerRuleData.outputId
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
