import { WorkspaceSecrets as WorkspaceSecretsClient } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { EntityNotFoundError } from "src/generators/errors";
import { ApiNode as ApiNodeType, NodeInput } from "src/types/vellum";

export class ApiNodeContext extends BaseNodeContext<ApiNodeType> {
  baseNodeClassName = "APINode";
  baseNodeDisplayClassName = "BaseAPINodeDisplay";

  getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.jsonOutputId]: "json",
      [this.nodeData.data.statusCodeOutputId]: "status_code",
      [this.nodeData.data.textOutputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
    };
  }

  protected createPortContexts(): PortContext[] {
    return [
      new PortContext({
        workflowContext: this.workflowContext,
        nodeContext: this,
        portId: this.nodeData.data.sourceHandleId,
      }),
    ];
  }

  private async processSecretInput(input: NodeInput): Promise<void> {
    const inputRule = input?.value.rules.find(
      (rule) => rule.type == "WORKSPACE_SECRET"
    );
    if (!inputRule || !inputRule.data?.workspaceSecretId) {
      return;
    }
    try {
      const tokenItem = await new WorkspaceSecretsClient({
        apiKey: this.workflowContext.vellumApiKey,
      }).retrieve(inputRule.data.workspaceSecretId);
      inputRule.data.workspaceSecretId = tokenItem.name;
    } catch (e) {
      if (e instanceof VellumError && e.statusCode === 404) {
        this.workflowContext.addError(
          new EntityNotFoundError(`Workspace Secret "${input.key}" not found.`)
        );
      } else {
        throw e;
      }
    }
  }

  async buildProperties(): Promise<void> {
    const apiKeyInputId = this.nodeData.data.apiKeyHeaderValueInputId;
    const apiKeyInput = this.nodeData.inputs.find(
      (input) => input.id === apiKeyInputId
    );

    const bearerKeyInputId = this.nodeData.data.bearerTokenValueInputId;
    const bearerKeyInput = this.nodeData.inputs.find(
      (input) => input.id === bearerKeyInputId
    );
    const secrets = [];
    secrets.push(apiKeyInput);
    secrets.push(bearerKeyInput);
    await Promise.all(
      secrets.map(async (input) => this.processSecretInput(input))
    );
  }
}
