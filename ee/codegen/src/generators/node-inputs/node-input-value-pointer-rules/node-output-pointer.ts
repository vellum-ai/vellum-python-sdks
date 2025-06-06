import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { NodeOutputPointer } from "src/types/vellum";

export class NodeOutputPointerRule extends BaseNodeInputValuePointerRule<NodeOutputPointer> {
  getReferencedNodeContext() {
    const nodeOutputPointerRuleData = this.nodeInputValuePointerRule.data;

    return this.workflowContext.findNodeContext(
      nodeOutputPointerRuleData.nodeId
    );
  }

  getAstNode(): python.AstNode | undefined {
    const nodeOutputPointerRuleData = this.nodeInputValuePointerRule.data;

    const nodeContext = this.getReferencedNodeContext();

    if (!nodeContext) {
      return undefined;
    }

    const nodeOutputName = nodeContext.getNodeOutputNameById(
      nodeOutputPointerRuleData.outputId
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
