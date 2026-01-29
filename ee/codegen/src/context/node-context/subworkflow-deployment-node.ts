import { VellumVariableType, WorkflowDeploymentRelease } from "vellum-ai/api";
import { WorkflowDeployments as WorkflowReleaseClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";
import { toValidPythonIdentifier } from "src/utils/casing";
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
    const deployedOutputVariables =
      this.workflowDeploymentRelease.workflowVersion.outputVariables;

    // Build a mapping from deployed workflow output variable IDs to their names
    const result = deployedOutputVariables.reduce<Record<string, string>>(
      (acc, output) => {
        acc[output.id] = toValidPythonIdentifier(output.key, "output");
        return acc;
      },
      { ...(errorOutputId ? { [errorOutputId]: "error" } : {}) }
    );

    // Also map workflow output variable IDs to deployed workflow output variable names
    // This handles the case where a TERMINAL node references a SUBWORKFLOW deployment node's
    // output using the workflow's output variable ID instead of the deployed workflow's output variable ID
    const deployedOutputsByKey = new Map(
      deployedOutputVariables.map((output) => [
        output.key,
        toValidPythonIdentifier(output.key, "output"),
      ])
    );

    for (const outputVariableContext of this.workflowContext.outputVariableContextsById.values()) {
      const workflowOutputKey = outputVariableContext.getRawName();
      const deployedOutputName = deployedOutputsByKey.get(workflowOutputKey);
      if (deployedOutputName) {
        const workflowOutputId = outputVariableContext.getOutputVariableId();
        // Only add if not already present (deployed workflow's ID takes precedence)
        if (!result[workflowOutputId]) {
          result[workflowOutputId] = deployedOutputName;
        }
      }
    }

    return result;
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    if (!this.workflowDeploymentRelease) {
      return {};
    }

    const deployedOutputVariables =
      this.workflowDeploymentRelease.workflowVersion.outputVariables;

    // Build a mapping from deployed workflow output variable IDs to their types
    const result = Object.fromEntries(
      deployedOutputVariables.map((variable) => [variable.id, variable.type])
    );

    // Also map workflow output variable IDs to deployed workflow output variable types
    // This handles the case where a TERMINAL node references a SUBWORKFLOW deployment node's
    // output using the workflow's output variable ID instead of the deployed workflow's output variable ID
    const deployedOutputTypesByKey = new Map(
      deployedOutputVariables.map((output) => [output.key, output.type])
    );

    for (const outputVariableContext of this.workflowContext.outputVariableContextsById.values()) {
      const workflowOutputKey = outputVariableContext.getRawName();
      const deployedOutputType =
        deployedOutputTypesByKey.get(workflowOutputKey);
      if (deployedOutputType) {
        const workflowOutputId = outputVariableContext.getOutputVariableId();
        // Only add if not already present (deployed workflow's ID takes precedence)
        if (!result[workflowOutputId]) {
          result[workflowOutputId] = deployedOutputType;
        }
      }
    }

    return result;
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
      const requestOptions = {
        headers: {
          "X-Vellum-Is-Workspace-Auth": "true",
        },
      };

      this.workflowDeploymentRelease = await new WorkflowReleaseClient({
        apiKey: this.workflowContext.vellumApiKey,
        environment: this.workflowContext.vellumApiEnvironment,
      }).retrieveWorkflowDeploymentRelease(
        this.nodeData.data.workflowDeploymentId,
        this.nodeData.data.releaseTag,
        requestOptions
      );
    } catch (error) {
      if (isVellumErrorWithDetail(error)) {
        throw new NodeDefinitionGenerationError(error.body.detail, "WARNING");
      }

      throw error;
    }
  }
}
