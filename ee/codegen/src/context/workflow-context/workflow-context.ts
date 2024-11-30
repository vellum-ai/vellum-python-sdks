import { MlModels } from "vellum-ai/api/resources/mlModels/client/Client";

import { GENERATED_WORKFLOW_MODULE_NAME } from "src/constants";
import { InputVariableContext } from "src/context/input-variable-context";
import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { generateSdkModulePaths } from "src/context/workflow-context/sdk-module-paths";
import { SDK_MODULE_PATHS } from "src/context/workflow-context/types";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { BaseNode } from "src/generators/nodes/bases";
import {
  EntrypointNode,
  WorkflowDataNode,
  WorkflowEdge,
} from "src/types/vellum";
import { createPythonClassName } from "src/utils/casing";

type InputVariableContextsById = Map<string, InputVariableContext>;

type NodeContextsByNodeId = Map<string, BaseNodeContext<WorkflowDataNode>>;

// A mapping between source handle ids and port contexts
type PortContextById = Map<string, PortContext>;

export declare namespace WorkflowContext {
  export type Args = {
    absolutePathToOutputDirectory: string;
    moduleName: string;
    workflowLabel?: string;
    workflowClassName?: string;
    inputVariableContextsById?: InputVariableContextsById;
    nodeContextsByNodeId?: NodeContextsByNodeId;
    parentNode?: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowsSdkModulePath?: readonly string[];
    portContextByName?: PortContextById;
    vellumApiKey: string;
    workflowRawEdges: WorkflowEdge[];
  };
}

export class WorkflowContext {
  public readonly absolutePathToOutputDirectory: string;
  public readonly modulePath: string[];
  public readonly moduleName: string;
  public readonly label: string | undefined;
  public readonly workflowClassName: string;

  // Maps workflow input variable IDs to the input variable
  public readonly inputVariableContextsById: InputVariableContextsById;

  // A list of all outputs this workflow produces
  public readonly workflowOutputContexts: WorkflowOutputContext[] = [];

  // Maps node IDs to a mapping of output IDs to output names
  public readonly nodeContextsByNodeId: NodeContextsByNodeId;

  // If this workflow is a nested workflow belonging to a node, track that node's context here.
  public readonly parentNode?: BaseNode<
    WorkflowDataNode,
    BaseNodeContext<WorkflowDataNode>
  >;

  // The entrypoint node for this workflow
  private entrypointNode: EntrypointNode | undefined;

  public readonly sdkModulePathNames: SDK_MODULE_PATHS;

  public readonly portContextById: PortContextById;

  // Used by the vellum api client
  public readonly vellumApiKey: string;
  private readonly mlModelNamesById: Record<string, string> = {};

  public readonly workflowRawEdges: WorkflowEdge[];

  constructor({
    absolutePathToOutputDirectory,
    moduleName,
    workflowLabel,
    workflowClassName,
    inputVariableContextsById,
    nodeContextsByNodeId,
    parentNode,
    workflowsSdkModulePath = ["vellum", "workflows"] as const,
    portContextByName,
    vellumApiKey,
    workflowRawEdges,
  }: WorkflowContext.Args) {
    this.absolutePathToOutputDirectory = absolutePathToOutputDirectory;
    this.moduleName = moduleName;
    this.modulePath = parentNode
      ? [
          ...parentNode.nodeContext.nodeModulePath,
          GENERATED_WORKFLOW_MODULE_NAME,
        ]
      : [this.moduleName, GENERATED_WORKFLOW_MODULE_NAME];
    this.label = workflowLabel || "Workflow";
    this.workflowClassName =
      workflowClassName || createPythonClassName(this.label);
    this.vellumApiKey = vellumApiKey;

    this.inputVariableContextsById = inputVariableContextsById ?? new Map();
    this.nodeContextsByNodeId = nodeContextsByNodeId ?? new Map();
    this.portContextById = portContextByName ?? new Map();

    this.parentNode = parentNode;

    this.sdkModulePathNames = generateSdkModulePaths(workflowsSdkModulePath);
    this.workflowRawEdges = workflowRawEdges;
  }

  /* Create a new workflow context for a nested workflow from its parent */
  public createNestedWorkflowContext({
    workflowLabel,
    parentNode,
    workflowRawEdges,
  }: {
    workflowLabel: string;
    parentNode: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowRawEdges: WorkflowEdge[];
  }) {
    return new WorkflowContext({
      absolutePathToOutputDirectory: this.absolutePathToOutputDirectory,
      moduleName: this.moduleName,
      workflowLabel,
      inputVariableContextsById: this.inputVariableContextsById,
      nodeContextsByNodeId: this.nodeContextsByNodeId,
      parentNode,
      workflowsSdkModulePath: this.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      vellumApiKey: this.vellumApiKey,
      workflowRawEdges,
    });
  }

  public addEntrypointNode(entrypointNode: EntrypointNode): void {
    if (this.entrypointNode) {
      throw new Error("Entrypoint node already exists");
    }

    this.entrypointNode = entrypointNode;
  }

  public getEntrypointNode(): EntrypointNode {
    if (!this.entrypointNode) {
      throw new Error("Entrypoint node not found");
    }

    return this.entrypointNode;
  }

  public addInputVariableContext(
    inputVariableContext: InputVariableContext
  ): void {
    const inputVariableId = inputVariableContext.getInputVariableId();
    this.inputVariableContextsById.set(inputVariableId, inputVariableContext);
  }

  public getInputVariableContextById(
    inputVariableId: string
  ): InputVariableContext {
    const inputVariableContext =
      this.inputVariableContextsById.get(inputVariableId);

    if (!inputVariableContext) {
      throw new Error(
        `Input variable context not found for ID: ${inputVariableId}`
      );
    }

    return inputVariableContext;
  }

  public addWorkflowOutputContext(
    workflowOutputContext: WorkflowOutputContext
  ): void {
    this.workflowOutputContexts.push(workflowOutputContext);
  }

  public addNodeContext(nodeContext: BaseNodeContext<WorkflowDataNode>): void {
    const nodeId = nodeContext.getNodeId();

    if (this.nodeContextsByNodeId.get(nodeId)) {
      throw new Error(`Node context already exists for node ID: ${nodeId}`);
    }

    this.nodeContextsByNodeId.set(nodeId, nodeContext);
  }

  public getNodeContext<T extends WorkflowDataNode>(
    nodeId: string
  ): BaseNodeContext<T> {
    const nodeContext = this.nodeContextsByNodeId.get(nodeId);

    if (!nodeContext) {
      throw new Error(`Node context not found for node ID: ${nodeId}`);
    }

    return nodeContext as BaseNodeContext<T>;
  }

  public addPortContext(portContext: PortContext): void {
    const portId = portContext.portId;

    if (this.portContextById.get(portId)) {
      throw new Error(`Port context already exists for port id: ${portId}`);
    }
    this.portContextById.set(portId, portContext);
  }

  public getPortContextById(portId: string): PortContext {
    const portContext: PortContext | undefined =
      this.portContextById.get(portId);

    if (!portContext) {
      throw new Error(`Port context not found for port id: ${portId}`);
    }

    return portContext;
  }

  public async getMLModelNameById(mlModelId: string): Promise<string> {
    if (this.mlModelNamesById[mlModelId]) {
      return this.mlModelNamesById[mlModelId];
    }

    const mlModel = await new MlModels({ apiKey: this.vellumApiKey }).retrieve(
      mlModelId
    );

    this.mlModelNamesById[mlModelId] = mlModel.name;
    return mlModel.name;
  }

  public addWorkflowEdges(edges: WorkflowEdge[]): void {
    this.workflowRawEdges.push(...edges);
  }
}
