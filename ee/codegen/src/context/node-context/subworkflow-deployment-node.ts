import { VellumVariableType, WorkflowDeploymentRelease } from "vellum-ai/api";
import { ReleaseReviews as WorkflowReleaseClient } from "vellum-ai/api/resources/releaseReviews/client/Client";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCaseWithCasePreservation } from "src/utils/casing";
import { isVellumErrorWithDetail } from "src/utils/nodes";

export class SubworkflowDeploymentNodeContext extends BaseNodeContext<SubworkflowNodeType> {
  baseNodeClassName = "SubworkflowDeploymentNode";
  baseNodeDisplayClassName = "BaseSubworkflowDeploymentNodeDisplay";

  public workflowDeploymentRelease: WorkflowDeploymentRelease | null = null;

  getNodeOutputNamesById(): Record<string, string> {
    if (!this.workflowDeploymentRelease) {
      return {};
    }

    const errorOutputId = this.getErrorOutputId();
    return this.workflowDeploymentRelease.workflowVersion.outputVariables.reduce<
      Record<string, string>
    >(
      (acc, output) => {
        acc[output.id] = toPythonSafeSnakeCaseWithCasePreservation(output.key, "output");
        return acc;
      },
      { ...(errorOutputId ? { [errorOutputId]: "error" } : {}) }
    );
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    if (!this.workflowDeploymentRelease) {
      return {};
    }

    return Object.fromEntries(
      this.workflowDeploymentRelease.workflowVersion.outputVariables.map(
        (variable) => [variable.id, variable.type]
      )
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
    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      return;
    }

    try {
      this.workflowDeploymentRelease = await new WorkflowReleaseClient({
        apiKey: this.workflowContext.vellumApiKey,
        environment: this.workflowContext.vellumApiEnvironment,
      }).retrieveWorkflowDeploymentRelease(
        this.nodeData.data.workflowDeploymentId,
        this.nodeData.data.releaseTag
      );
    } catch (error) {
      if (isVellumErrorWithDetail(error)) {
        throw new NodeDefinitionGenerationError(error.body.detail, "WARNING");
      }

      throw error;
    }
  }
}
