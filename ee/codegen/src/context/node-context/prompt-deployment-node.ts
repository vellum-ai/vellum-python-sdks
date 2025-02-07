import { DeploymentHistoryItem } from "vellum-ai/api";
import { Deployments as DeploymentsClient } from "vellum-ai/api/resources/deployments/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { PromptNode } from "src/types/vellum";

export class PromptDeploymentNodeContext extends BaseNodeContext<PromptNode> {
  baseNodeClassName = "PromptDeploymentNode";
  baseNodeDisplayClassName = "BasePromptDeploymentNodeDisplay";

  public deploymentHistoryItem: DeploymentHistoryItem | null = null;

  protected getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.outputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
      [this.nodeData.data.arrayOutputId]: "results",
    };
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
      this.deploymentHistoryItem = await new DeploymentsClient({
        apiKey: this.workflowContext.vellumApiKey,
      }).deploymentHistoryItemRetrieve(
        this.nodeData.data.releaseTag,
        this.nodeData.data.promptDeploymentId
      );
    } catch (error) {
      if (
        error instanceof VellumError &&
        typeof error.body === "object" &&
        error.body !== null &&
        "detail" in error.body &&
        typeof error.body.detail === "string"
      ) {
        throw new NodeDefinitionGenerationError(error.body.detail);
      } else {
        throw error;
      }
    }
  }
}
