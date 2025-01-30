import { WorkspaceSecretRead } from "vellum-ai/api";
import { WorkspaceSecrets as WorkspaceSecretsClient } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { EntityNotFoundError } from "src/generators/errors";
import { ApiNode as ApiNodeType } from "src/types/vellum";

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

  async buildProperties(): Promise<void> {
    let apiTokenItem: WorkspaceSecretRead | undefined = undefined;
    let bearerTokenItem: WorkspaceSecretRead | undefined = undefined;

    try {
      const apiKeyInputId = this.nodeData.data.apiKeyHeaderValueInputId;
      const apiKeyInput = this.nodeData.inputs.find(
        (input) => input.id === apiKeyInputId
      );

      const apiKeyInputRule = apiKeyInput?.value.rules.find(
        (rule) => rule.type == "WORKSPACE_SECRET"
      );
      if (apiKeyInputRule && apiKeyInputRule.data?.workspaceSecretId) {
        apiTokenItem = await new WorkspaceSecretsClient({
          apiKey: this.workflowContext.vellumApiKey,
        }).retrieve(apiKeyInputRule.data?.workspaceSecretId);
        apiKeyInputRule.data.workspaceSecretId = apiTokenItem.name;
      }
    } catch (e) {
      if (e instanceof VellumError && e.statusCode === 404) {
        this.workflowContext.addError(
          new EntityNotFoundError(
            `Workspace Secret "${this.nodeData.data.apiKeyHeaderValueInputId}" not found.`
          )
        );
      } else {
        throw e;
      }
    }

    try {
      const bearerKeyInputId = this.nodeData.data.bearerTokenValueInputId;
      const bearerKeyInput = this.nodeData.inputs.find(
        (input) => input.id === bearerKeyInputId
      );

      const bearerKeyInputRule = bearerKeyInput?.value.rules.find(
        (rule) => rule.type == "WORKSPACE_SECRET"
      );
      if (bearerKeyInputRule && bearerKeyInputRule.data?.workspaceSecretId) {
        bearerTokenItem = await new WorkspaceSecretsClient({
          apiKey: this.workflowContext.vellumApiKey,
        }).retrieve(bearerKeyInputRule.data?.workspaceSecretId);
        bearerKeyInputRule.data.workspaceSecretId = bearerTokenItem.name;
      }
    } catch (e) {
      if (e instanceof VellumError && e.statusCode === 404) {
        this.workflowContext.addError(
          new EntityNotFoundError(
            `Workspace Secret "${this.nodeData.data.bearerTokenValueInputId}" not found.`
          )
        );
      } else {
        throw e;
      }
    }
  }
}
