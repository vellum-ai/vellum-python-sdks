import { DeploymentHistoryItem, VellumVariableType } from "vellum-ai/api";
import { Deployments as DeploymentsClient } from "vellum-ai/api/resources/deployments/client/Client";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { PromptNode } from "src/types/vellum";
import { isVellumErrorWithDetail } from "src/utils/nodes";

export class PromptDeploymentNodeContext extends BaseNodeContext<PromptNode> {
  baseNodeClassName = "PromptDeploymentNode";
  baseNodeDisplayClassName = "BasePromptDeploymentNodeDisplay";

  public deploymentHistoryItem: DeploymentHistoryItem | null = null;

  protected getNodeOutputNamesById(): Record<string, string> {
    const jsonOutput = this.nodeData.outputs?.find(
      (output) => output.type === "JSON"
    );
    return {
      [this.nodeData.data.outputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
      [this.nodeData.data.arrayOutputId]: "results",
      ...(jsonOutput ? { [jsonOutput.id]: "json" } : {}),
    };
  }

  protected getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.outputId]: "STRING",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "ERROR" }
        : {}),
      [this.nodeData.data.arrayOutputId]: "ARRAY",
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
        environment: this.workflowContext.vellumApiEnvironment,
      }).deploymentHistoryItemRetrieve(
        this.nodeData.data.releaseTag,
        this.nodeData.data.promptDeploymentId
      );
    } catch (error) {
      if (isVellumErrorWithDetail(error)) {
        this.workflowContext.addError(
          new NodeDefinitionGenerationError(
            `Could not find prompt deployment with id: ${this.nodeData.data.promptDeploymentId}, falling back to id`,
            "WARNING"
          )
        );
      } else {
        throw error;
      }
    }
  }
}
