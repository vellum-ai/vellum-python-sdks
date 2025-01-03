import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { NodeOutputPointer } from "src/types/vellum";

export class NodeOutputPointerRule extends BaseNodeInputValuePointerRule<NodeOutputPointer> {
  getAstNode(): python.Reference {
    const nodeOutputPointerRuleData = this.nodeInputValuePointerRule.data;

    const nodeContext = this.workflowContext.getNodeContext(
      nodeOutputPointerRuleData.nodeId
    );

    const nodeOutputName = nodeContext.getNodeOutputNameById(
      nodeOutputPointerRuleData.outputId
    );

    return python.reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: [OUTPUTS_CLASS_NAME, nodeOutputName],
    });
  }
}
