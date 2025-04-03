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
    return this.nodeData.data.conditions.map(
      (condition, idx) =>
        new PortContext({
          workflowContext: this.workflowContext,
          nodeContext: this,
          portId: condition.sourceHandleId,
          portName: `branch_${idx + 1}`,
          isDefault: false,
        })
    );
  }
}
