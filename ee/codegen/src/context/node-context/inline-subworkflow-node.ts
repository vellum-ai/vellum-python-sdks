import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";

export class InlineSubworkflowNodeContext extends BaseNodeContext<SubworkflowNodeType> {
  baseNodeClassName = "InlineSubworkflowNode";
  baseNodeDisplayClassName = "BaseInlineSubworkflowNodeDisplay";
  isCore = true;

  getNodeOutputNamesById(): Record<string, string> {
    const subworkflowNodeData = this.nodeData.data;
    if (subworkflowNodeData.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    return subworkflowNodeData.outputVariables.reduce((acc, variable) => {
      acc[variable.id] = variable.key;
      return acc;
    }, {} as Record<string, string>);
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    const subworkflowNodeData = this.nodeData.data;
    if (subworkflowNodeData.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    return Object.fromEntries(
      subworkflowNodeData.outputVariables.map((variable) => [
        variable.id,
        variable.type,
      ])
    );
  }

  createPortContexts(): PortContext[] {
    return [
      new PortContext({
        workflowContext: this.workflowContext,
        nodeContext: this,
        portId: this.nodeData.data.sourceHandleId,
      }),
    ];
  }
}
