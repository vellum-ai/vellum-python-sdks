import { MetricDefinitionHistoryItem, VellumVariableType } from "vellum-ai/api";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { EntityNotFoundError } from "src/generators/errors";
import { GuardrailNode as GuardrailNodeType } from "src/types/vellum";

export class GuardrailNodeContext extends BaseNodeContext<GuardrailNodeType> {
  baseNodeClassName = "GuardrailNode";
  baseNodeDisplayClassName = "BaseGuardrailNodeDisplay";

  public metricDefinitionsHistoryItem: MetricDefinitionHistoryItem | undefined =
    undefined;

  getNodeOutputNamesById(): Record<string, string> {
    if (!this.metricDefinitionsHistoryItem) {
      return {};
    }

    return this.metricDefinitionsHistoryItem.outputVariables.reduce(
      (acc, variable) => {
        acc[variable.id] = variable.key;
        return acc;
      },
      {} as Record<string, string>
    );
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    if (!this.metricDefinitionsHistoryItem) {
      return {};
    }

    return Object.fromEntries(
      this.metricDefinitionsHistoryItem.outputVariables.map((variable) => {
        // If the variable key is "score", hardcode the type to "NUMBER". We assume float on sdk side anyway
        if (variable.key === "score") {
          return [variable.id, "NUMBER"];
        }
        return [variable.id, variable.type];
      })
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
    let metricDefinitionsHistoryItem: MetricDefinitionHistoryItem | undefined =
      undefined;

    try {
      metricDefinitionsHistoryItem = await new MetricDefinitionsClient({
        apiKey: this.workflowContext.vellumApiKey,
        environment: this.workflowContext.vellumApiEnvironment,
      }).metricDefinitionHistoryItemRetrieve(
        this.nodeData.data.releaseTag,
        this.nodeData.data.metricDefinitionId
      );
    } catch (e) {
      if (e instanceof VellumError && e.statusCode === 404) {
        this.workflowContext.addError(
          new EntityNotFoundError(
            `Metric Definition "${this.nodeData.data.metricDefinitionId} ${this.nodeData.data.releaseTag}" not found.`,
            "WARNING"
          )
        );
      } else {
        throw e;
      }
    }

    this.metricDefinitionsHistoryItem = metricDefinitionsHistoryItem;
  }
}
