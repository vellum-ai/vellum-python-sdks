import { CodeExecutionRuntime, VellumVariableType } from "vellum-ai/api";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import {
  EntityNotFoundError,
  NodeAttributeGenerationError,
} from "src/generators/errors";
import {
  CodeExecutionNode as CodeExecutionNodeType,
  NodeInput,
  WorkspaceSecretPointer,
} from "src/types/vellum";

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

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.outputId]: this.nodeData.data.outputType,
      ...(this.nodeData.data.logOutputId
        ? { [this.nodeData.data.logOutputId]: "STRING" }
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

  public getRuntime(): CodeExecutionRuntime {
    const runtimeNodeInput = this.nodeData.inputs.find(
      (nodeInput) => nodeInput.key === "runtime"
    );

    const runtimeNodeInputRule = runtimeNodeInput?.value.rules[0];

    if (
      !runtimeNodeInputRule ||
      runtimeNodeInputRule.type !== "CONSTANT_VALUE" ||
      runtimeNodeInputRule.data.type !== "STRING"
    ) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Expected runtime node input to be a constant string value"
        )
      );
      return "PYTHON_3_11_6";
    }

    const runtime = runtimeNodeInputRule.data.value;
    if (runtime !== "PYTHON_3_11_6" && runtime !== "TYPESCRIPT_5_3_3") {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Unsupported runtime: ${runtime}`,
          "WARNING"
        )
      );
      return "PYTHON_3_11_6";
    }

    return runtime;
  }

  private getFilepath(): string {
    let filePath: string;
    if (this.nodeData.data.filepath) {
      filePath = this.nodeData.data.filepath;
    } else {
      const runtime = this.getRuntime();
      let filetype: string;
      if (runtime === "PYTHON_3_11_6") {
        filetype = "py";
      } else if (runtime === "TYPESCRIPT_5_3_3") {
        filetype = "ts";
      } else {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            `Unsupported runtime: ${runtime}`,
            "WARNING"
          )
        );
        filetype = "py";
      }
      filePath = `./script.${filetype}`;
    }

    return filePath;
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
            `Workspace Secret mapped to input "${input.key}" not found.`,
            "WARNING"
          )
        );
      } else {
        throw e;
      }
    }
  }

  async buildProperties(): Promise<void> {
    await Promise.all(
      this.nodeData.inputs.map(async (input) => this.processSecretInput(input))
    );
  }
}
