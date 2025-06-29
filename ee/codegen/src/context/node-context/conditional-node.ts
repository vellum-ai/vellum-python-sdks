import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { ConditionalNode } from "src/types/vellum";

export class ConditionalNodeContext extends BaseNodeContext<ConditionalNode> {
  baseNodeClassName = "ConditionalNode";
  baseNodeDisplayClassName = "BaseConditionalNodeDisplay";

  protected getNodeOutputNamesById(): Record<string, string> {
    return {};
  }

  protected getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {};
  }

  createPortContexts(): PortContext[] {
    const conditionTypeCounts = new Map<string, number>();

    return this.nodeData.data.conditions.map(
      (condition, idx) => {
        const conditionType = condition.type;
        const currentCount = conditionTypeCounts.get(conditionType) || 0;
        conditionTypeCounts.set(conditionType, currentCount + 1);

        const portName = this.generateSemanticPortName(conditionType, currentCount + 1);

        return new PortContext({
          workflowContext: this.workflowContext,
          nodeContext: this,
          portId: condition.sourceHandleId,
          portName: portName,
          isDefault: false,
        });
      }
    );
  }

  private generateSemanticPortName(conditionType: string, index: number): string {
    switch (conditionType) {
      case "IF":
        return `if_${index}`;
      case "ELIF":
        return `elif_${index}`;
      case "ELSE":
        return `else_${index}`;
      default:
        return `branch_${index}`;
    }
  }
}
