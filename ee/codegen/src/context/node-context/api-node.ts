import { VellumVariableType } from "vellum-ai/api";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import {
  EntityNotFoundError,
  NodeAttributeGenerationError,
} from "src/generators/errors";
import {
  ApiNode as ApiNodeType,
  NodeInput,
  WorkspaceSecretPointer,
} from "src/types/vellum";

export class ApiNodeContext extends BaseNodeContext<ApiNodeType> {
  baseNodeClassName = "APINode";
  baseNodeDisplayClassName = "BaseAPINodeDisplay";

  getNodeOutputNamesById(): Record<string, string> {
    const errorOutputId = this.getErrorOutputId();
    return {
      [this.nodeData.data.jsonOutputId]: "json",
      [this.nodeData.data.statusCodeOutputId]: "status_code",
      [this.nodeData.data.textOutputId]: "text",
      ...(errorOutputId ? { [errorOutputId]: "error" } : {}),
    };
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.jsonOutputId]: "JSON",
      [this.nodeData.data.statusCodeOutputId]: "NUMBER",
      [this.nodeData.data.textOutputId]: "STRING",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "ERROR" }
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
      (rule): rule is WorkspaceSecretPointer => rule.type == "WORKSPACE_SECRET"
    );
    if (!inputRule || !inputRule.data?.workspaceSecretId) {
      return;
    }
    try {
      await this.workflowContext.loadWorkspaceSecret(
        inputRule.data.workspaceSecretId
      );
    } catch (e) {
      if (e instanceof VellumError && e.statusCode === 404) {
        this.workflowContext.addError(
          new EntityNotFoundError(
            `Workspace Secret for attribute "${input.key}" not found.`,
            "WARNING"
          )
        );
      } else {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            `Failed to load workspace secret for attribute "${input.key}".`,
            "WARNING"
          )
        );
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
    if (apiKeyInput) {
      secrets.push(apiKeyInput);
    }
    if (bearerKeyInput) {
      secrets.push(bearerKeyInput);
    }

    this.nodeData.data.additionalHeaders?.forEach((header) => {
      const headerInputValue = this.nodeData.inputs.find(
        (input) => input.id === header.headerValueInputId
      );
      if (headerInputValue) {
        secrets.push(headerInputValue);
      }
    });
    await Promise.all(
      secrets.map(async (input) => this.processSecretInput(input))
    );
  }
}
