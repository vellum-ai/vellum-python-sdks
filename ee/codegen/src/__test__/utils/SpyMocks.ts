import { MetricDefinitionHistoryItem } from "vellum-ai/api";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { WorkflowDeployments as WorkflowReleaseClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";
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
        WorkflowReleaseClient.prototype,
        "retrieveWorkflowDeploymentRelease"
      )
      .mockResolvedValue({
        id: "mocked-workflow-deployment-history-item-id",
        created: new Date(),
        environment: {
          id: "mocked-environment-id",
          name: "mocked-environment-name",
          label: "mocked-environment-label",
        },
        createdBy: {
          id: "mocked-created-by-id",
          email: "mocked-created-by-email",
        },
        workflowVersion: {
          id: "mocked-workflow-release-id",
          inputVariables: [],
          outputVariables: [
            {
              id: "53970e88-0bf6-4364-86b3-840d78a2afe5",
              key: "chat_history",
              type: "STRING",
            },
          ],
        },
        deployment: {
          name: "mocked-workflow-deployment-release-name",
        },
        releaseTags: [
          {
            name: "mocked-release-tag-name",
            source: "USER",
          },
        ],
        reviews: [
          {
            id: "mocked-release-review-id",
            created: new Date(),
            reviewer: {
              id: "mocked-reviewer-id",
            },
            state: "APPROVED",
          },
        ],
      });
  }
}
