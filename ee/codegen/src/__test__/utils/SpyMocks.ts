import { MetricDefinitionHistoryItem } from "vellum-ai/api";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
import { MockInstance, vi } from "vitest";

export class SpyMocks {
  static createMetricDefinitionMock(): MockInstance {
    return vi
      .spyOn(
        MetricDefinitionsClient.prototype,
        "metricDefinitionHistoryItemRetrieve"
      )
      .mockResolvedValue({
        id: "mocked-metric-output-id",
        label: "mocked-metric-output-label",
        name: "mocked-metric-output-name",
        description: "mocked-metric-output-description",
        outputVariables: [
          {
            id: "0e455862-ccc4-47a4-a9a5-061fadc94fd6",
            key: "score",
            type: "NUMBER",
          },
        ],
      } as MetricDefinitionHistoryItem);
  }

  static createWorkflowDeploymentsMock(): MockInstance {
    return vi
      .spyOn(
        WorkflowDeploymentsClient.prototype,
        "workflowDeploymentHistoryItemRetrieve"
      )
      .mockResolvedValue({
        id: "mocked-workflow-deployment-history-item-id",
        workflowDeploymentId: "mocked-workflow-deployment-id",
        timestamp: new Date(),
        label: "mocked-workflow-deployment-history-item-label",
        name: "mocked-workflow-deployment-history-item-name",
        inputVariables: [],
        outputVariables: [
          {
            id: "53970e88-0bf6-4364-86b3-840d78a2afe5",
            key: "chat_history",
            type: "STRING",
          },
        ],
      });
  }
}
