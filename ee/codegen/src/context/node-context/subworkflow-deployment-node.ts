import {
  VellumVariableType,
  WorkflowDeploymentHistoryItem,
} from "vellum-ai/api";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";
import { isVellumErrorWithDetail } from "src/utils/nodes";

export class SubworkflowDeploymentNodeContext extends BaseNodeContext<SubworkflowNodeType> {
  baseNodeClassName = "SubworkflowDeploymentNode";
  baseNodeDisplayClassName = "BaseSubworkflowDeploymentNodeDisplay";

  public workflowDeploymentHistoryItem: WorkflowDeploymentHistoryItem | null =
    null;

  getNodeOutputNamesById(): Record<string, string> {
    if (!this.workflowDeploymentHistoryItem) {
      return {};
    }

    return this.workflowDeploymentHistoryItem.outputVariables.reduce<
      Record<string, string>
    >((acc, output) => {
      acc[output.id] = toPythonSafeSnakeCase(output.key, "output");
      return acc;
    }, {});
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    if (!this.workflowDeploymentHistoryItem) {
      return {};
    }

    return Object.fromEntries(
      this.workflowDeploymentHistoryItem.outputVariables.map((variable) => [
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

  async buildProperties(): Promise<void> {
    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      return;
    }

    try {
      this.workflowDeploymentHistoryItem = await new WorkflowDeploymentsClient({
        apiKey: this.workflowContext.vellumApiKey,
        environment: this.workflowContext.vellumApiEnvironment,
      }).workflowDeploymentHistoryItemRetrieve(
        this.nodeData.data.releaseTag,
        this.nodeData.data.workflowDeploymentId
      );
    } catch (error) {
      if (isVellumErrorWithDetail(error)) {
        throw new NodeDefinitionGenerationError(error.body.detail, "WARNING");
      }

      throw error;
    }
  }
}
