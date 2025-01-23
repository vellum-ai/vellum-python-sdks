import { WorkflowDeploymentHistoryItem } from "vellum-ai/api";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

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

    this.workflowDeploymentHistoryItem = await new WorkflowDeploymentsClient({
      apiKey: this.workflowContext.vellumApiKey,
    }).workflowDeploymentHistoryItemRetrieve(
      this.nodeData.data.releaseTag,
      this.nodeData.data.workflowDeploymentId
    );
  }
}
