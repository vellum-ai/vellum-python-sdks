import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import {
  InlinePromptNodeData,
  InlinePromptNode as InlinePromptNodeType,
  LegacyPromptNodeData,
} from "src/types/vellum";

export class InlinePromptNodeContext extends BaseNodeContext<InlinePromptNodeType> {
  baseNodeClassName = "InlinePromptNode";
  baseNodeDisplayClassName = "BaseInlinePromptNodeDisplay";

  public getNodeOutputNamesById(): Record<string, string> {
    const jsonOutput = this.nodeData.outputs?.find(
      (output) => output.type === "JSON"
    );
    const errorOutputId = this.getErrorOutputId();

    return {
      [this.nodeData.data.outputId]: "text",
      ...(errorOutputId ? { [errorOutputId]: "error" } : {}),
      [this.nodeData.data.arrayOutputId]: "results",
      ...(jsonOutput ? { [jsonOutput.id]: "json" } : {}),
    };
  }

  protected getNodeOutputTypesById(): Record<string, VellumVariableType> {
    const jsonOutput = this.nodeData.outputs?.find(
      (output) => output.type === "JSON"
    );

    return {
      [this.nodeData.data.outputId]: "STRING",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "ERROR" }
        : {}),
      [this.nodeData.data.arrayOutputId]: "ARRAY",
      ...(jsonOutput ? { [jsonOutput.id]: "JSON" } : {}),
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
    // @ts-expect-error In the legacy case, we simply convert from LEGACY to INLINE on the fly after the context is initialized with the legacy node data.
    if (this.nodeData.data.variant !== "LEGACY") {
      return;
    }

    // @ts-expect-error
    const legacyNodeData: LegacyPromptNodeData = this.nodeData.data;

    const promptVersionData =
      legacyNodeData.sandboxRoutingConfig.promptVersionData;
    if (!promptVersionData) {
      throw new NodeDefinitionGenerationError(`Prompt version data not found`);
    }

    // Dynamically fetch the ML Model's name via API
    const mlModelName = await this.workflowContext
      .getMLModelNameById(promptVersionData.mlModelToWorkspaceId)
      .catch((error) => {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            `Failed to fetch ML model name for ID ${promptVersionData.mlModelToWorkspaceId}: ${error}`,
            "WARNING"
          )
        );
        return "";
      });

    const inlinePromptNodeData: InlinePromptNodeData = {
      ...legacyNodeData,
      variant: "INLINE",
      mlModelName,
      execConfig: promptVersionData.execConfig,
    };

    this.nodeData = { ...this.nodeData, data: inlinePromptNodeData };
  }
}
