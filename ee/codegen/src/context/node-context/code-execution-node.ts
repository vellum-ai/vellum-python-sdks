import { WorkspaceSecrets as WorkspaceSecretsClient } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import {
  EntityNotFoundError,
  NodeAttributeGenerationError,
} from "src/generators/errors";
import { CodeExecutionNode as CodeExecutionNodeType } from "src/types/vellum";

export class CodeExecutionContext extends BaseNodeContext<CodeExecutionNodeType> {
  baseNodeClassName = "CodeExecutionNode";
  baseNodeDisplayClassName = "BaseCodeExecutionNodeDisplay";

  public readonly filepath: string;

  constructor(args: BaseNodeContext.Args<CodeExecutionNodeType>) {
    super(args);

    this.filepath = this.getFilepath();
  }

  getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.outputId]: "result",
      ...(this.nodeData.data.logOutputId
        ? { [this.nodeData.data.logOutputId]: "logs" }
        : {}),
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

  private getFilepath(): string {
    let filePath: string;
    if (this.nodeData.data.filepath) {
      filePath = this.nodeData.data.filepath;
    } else {
      const runtimeNodeInput = this.nodeData.inputs.find(
        (nodeInput) => nodeInput.key === "runtime"
      );

      const runtimeNodeInputRule = runtimeNodeInput?.value.rules[0];

      if (
        !runtimeNodeInputRule ||
        runtimeNodeInputRule.type !== "CONSTANT_VALUE" ||
        runtimeNodeInputRule.data.type !== "STRING"
      ) {
        throw new NodeAttributeGenerationError(
          "Expected runtime node input to be a constant string value"
        );
      }

      const runtime = runtimeNodeInputRule.data.value;
      let filetype: string;
      if (runtime?.includes("PYTHON")) {
        filetype = "py";
      } else if (runtime?.includes("TYPESCRIPT")) {
        filetype = "ts";
      } else {
        throw new NodeAttributeGenerationError(
          `Unsupported runtime: ${runtime}`
        );
      }
      filePath = `./script.${filetype}`;
    }

    return filePath;
  }

  async buildProperties(): Promise<void> {
    for (const input of this.nodeData.inputs) {
      try {
        const inputRule = input?.value.rules.find(
          (rule) => rule.type == "WORKSPACE_SECRET"
        );
        if (inputRule && inputRule.data?.workspaceSecretId) {
          const tokenItem = await new WorkspaceSecretsClient({
            apiKey: this.workflowContext.vellumApiKey,
          }).retrieve(inputRule.data?.workspaceSecretId);
          inputRule.data.workspaceSecretId = tokenItem.name;
        }
      } catch (e) {
        if (e instanceof VellumError && e.statusCode === 404) {
          this.workflowContext.addError(
            new EntityNotFoundError(`Workspace Secret "${input.id}" not found.`)
          );
        } else {
          throw e;
        }
      }
    }
  }
}
