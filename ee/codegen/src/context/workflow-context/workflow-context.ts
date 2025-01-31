import { MlModels } from "vellum-ai/api/resources/mlModels/client/Client";

import { GENERATED_WORKFLOW_MODULE_NAME } from "src/constants";
import { InputVariableContext } from "src/context/input-variable-context";
import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { generateSdkModulePaths } from "src/context/workflow-context/sdk-module-paths";
import { SDK_MODULE_PATHS } from "src/context/workflow-context/types";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import {
  BaseCodegenError,
  NodeDefinitionGenerationError,
  NodeNotFoundError,
  NodePortGenerationError,
  WorkflowGenerationError,
  WorkflowInputGenerationError,
} from "src/generators/errors";
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
    workflowClassName: string;
    globalInputVariableContextsById?: InputVariableContextsById;
    globalNodeContextsByNodeId?: NodeContextsByNodeId;
    parentNode?: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowsSdkModulePath?: readonly string[];
    portContextByName?: PortContextById;
    vellumApiKey: string;
    workflowRawEdges: WorkflowEdge[];
    strict?: boolean;
    codeExecutionNodeCodeRepresentationOverride?: "STANDALONE" | "INLINE";
  };
}

export class WorkflowContext {
  public readonly absolutePathToOutputDirectory: string;
  public readonly modulePath: string[];
  public readonly moduleName: string;
  public readonly label: string | undefined;
  public readonly workflowClassName: string;

  // Maps workflow input variable IDs to the input variable
  // Tracks local and global contexts in the case of nested workflows.
  public readonly inputVariableContextsById: InputVariableContextsById;
  public readonly globalInputVariableContextsById: InputVariableContextsById;
  public readonly strict: boolean;

  // Track what input variables names are used within this workflow so that we can ensure name uniqueness when adding
  // new input variables.
  private readonly inputVariableNames: Set<string> = new Set();

  // Maps node IDs to a mapping of output IDs to output names.
  // Tracks local and global contexts in the case of nested workflows.
  public readonly nodeContextsByNodeId: NodeContextsByNodeId;
  public readonly globalNodeContextsByNodeId: NodeContextsByNodeId;

  // Track what node module names are used within this workflow so that we can ensure name uniqueness when adding
  // new nodes.
  private readonly nodeModuleNames: Set<string> = new Set();

  // A list of all outputs this workflow produces
  public readonly workflowOutputContexts: WorkflowOutputContext[] = [];

  // Track what output variables names are used within this workflow so that we can ensure name uniqueness when adding
  // new output variables.
  private readonly outputVariableNames: Set<string> = new Set();

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
  private readonly errors: BaseCodegenError[] = [];

  public readonly workflowRawEdges: WorkflowEdge[];

  public readonly codeExecutionNodeCodeRepresentationOverride:
    | "STANDALONE"
    | "INLINE"
    | undefined;

  // Track what class names are used within this workflow so that we can ensure name uniqueness
  private readonly classNames: Set<string> = new Set();

  constructor({
    absolutePathToOutputDirectory,
    moduleName,
    workflowClassName,
    globalInputVariableContextsById,
    globalNodeContextsByNodeId,
    parentNode,
    workflowsSdkModulePath = ["vellum", "workflows"] as const,
    portContextByName,
    vellumApiKey,
    workflowRawEdges,
    strict = false,
    codeExecutionNodeCodeRepresentationOverride,
  }: WorkflowContext.Args) {
    this.absolutePathToOutputDirectory = absolutePathToOutputDirectory;
    this.moduleName = moduleName;
    this.modulePath = parentNode
      ? [
          ...parentNode.nodeContext.nodeModulePath,
          GENERATED_WORKFLOW_MODULE_NAME,
        ]
      : [this.moduleName, GENERATED_WORKFLOW_MODULE_NAME];
    this.workflowClassName = workflowClassName;
    this.vellumApiKey = vellumApiKey;

    this.inputVariableContextsById = new Map();
    this.globalInputVariableContextsById =
      globalInputVariableContextsById ?? new Map();

    this.nodeContextsByNodeId = new Map();
    this.globalNodeContextsByNodeId = globalNodeContextsByNodeId ?? new Map();

    this.portContextById = portContextByName ?? new Map();

    this.parentNode = parentNode;

    this.sdkModulePathNames = generateSdkModulePaths(workflowsSdkModulePath);
    this.workflowRawEdges = workflowRawEdges;

    this.strict = strict;
    this.errors = [];

    this.codeExecutionNodeCodeRepresentationOverride =
      codeExecutionNodeCodeRepresentationOverride;
  }

  /* Create a new workflow context for a nested workflow from its parent */
  public createNestedWorkflowContext({
    parentNode,
    workflowClassName,
    workflowRawEdges,
  }: {
    parentNode: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowClassName: string;
    workflowRawEdges: WorkflowEdge[];
  }) {
    return new WorkflowContext({
      absolutePathToOutputDirectory: this.absolutePathToOutputDirectory,
      moduleName: this.moduleName,
      workflowClassName: workflowClassName,
      globalInputVariableContextsById: this.globalInputVariableContextsById,
      globalNodeContextsByNodeId: this.globalNodeContextsByNodeId,
      parentNode,
      workflowsSdkModulePath: this.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      vellumApiKey: this.vellumApiKey,
      workflowRawEdges,
      codeExecutionNodeCodeRepresentationOverride:
        this.codeExecutionNodeCodeRepresentationOverride,
    });
  }

  public addEntrypointNode(entrypointNode: EntrypointNode): void {
    if (this.entrypointNode) {
      throw new WorkflowGenerationError("Entrypoint node already exists");
    }

    this.entrypointNode = entrypointNode;
  }

  public getEntrypointNode(): EntrypointNode {
    if (!this.entrypointNode) {
      throw new WorkflowGenerationError("Entrypoint node not found");
    }

    return this.entrypointNode;
  }

  public getEntrypointNodeEdges(): WorkflowEdge[] {
    const entrypointNodeId = this.getEntrypointNode().id;
    return this.workflowRawEdges.filter(
      (edge) => edge.sourceNodeId === entrypointNodeId
    );
  }

  public getEdgesByPortId(): Map<string, WorkflowEdge[]> {
    const edgesByPortId = new Map<string, WorkflowEdge[]>();
    this.workflowRawEdges.forEach((edge) => {
      const portId = edge.sourceHandleId;
      const edges = edgesByPortId.get(portId) ?? [];
      edges.push(edge);
      edgesByPortId.set(portId, edges);
    });
    return edgesByPortId;
  }

  public isInputVariableNameUsed(inputVariableName: string): boolean {
    return this.inputVariableNames.has(inputVariableName);
  }

  private addUsedInputVariableName(inputVariableName: string): void {
    this.inputVariableNames.add(inputVariableName);
  }

  public addInputVariableContext(
    inputVariableContext: InputVariableContext
  ): void {
    const inputVariableId = inputVariableContext.getInputVariableId();

    if (this.globalInputVariableContextsById.get(inputVariableId)) {
      throw new WorkflowInputGenerationError(
        `Input variable context already exists for input variable ID: ${inputVariableId}`
      );
    }

    this.inputVariableContextsById.set(inputVariableId, inputVariableContext);
    this.globalInputVariableContextsById.set(
      inputVariableId,
      inputVariableContext
    );
    this.addUsedInputVariableName(inputVariableContext.name);
  }

  public findInputVariableContextById(
    inputVariableId: string
  ): InputVariableContext | undefined {
    return this.globalInputVariableContextsById.get(inputVariableId);
  }

  public findInputVariableContextByRawName(
    rawName: string
  ): InputVariableContext | undefined {
    return Array.from(this.inputVariableContextsById.values()).find(
      (inputContext) => inputContext.getRawName() === rawName
    );
  }

  public getInputVariableContextByRawName(
    rawName: string
  ): InputVariableContext {
    const inputVariableContext =
      this.findInputVariableContextByRawName(rawName);

    if (!inputVariableContext) {
      throw new WorkflowInputGenerationError(
        `Input variable context not found for raw name: ${rawName}`
      );
    }

    return inputVariableContext;
  }

  public isOutputVariableNameUsed(outputVariableName: string): boolean {
    return this.outputVariableNames.has(outputVariableName);
  }

  private addUsedOutputVariableName(outputVariableName: string): void {
    this.outputVariableNames.add(outputVariableName);
  }

  public addWorkflowOutputContext(
    workflowOutputContext: WorkflowOutputContext
  ): void {
    this.workflowOutputContexts.push(workflowOutputContext);
    this.addUsedOutputVariableName(workflowOutputContext.name);
  }

  public isNodeModuleNameUsed(nodeModuleName: string): boolean {
    return this.nodeModuleNames.has(nodeModuleName);
  }

  private addUsedNodeModuleName(nodeModuleName: string): void {
    this.nodeModuleNames.add(nodeModuleName);
  }

  public addNodeContext(nodeContext: BaseNodeContext<WorkflowDataNode>): void {
    const nodeId = nodeContext.nodeData.id;

    if (this.globalNodeContextsByNodeId.get(nodeId)) {
      throw new NodeDefinitionGenerationError(
        `Node context already exists for node ID: ${nodeId}`
      );
    }

    this.nodeContextsByNodeId.set(nodeId, nodeContext);
    this.globalNodeContextsByNodeId.set(nodeId, nodeContext);
    this.addUsedNodeModuleName(nodeContext.nodeModuleName);
  }

  public getNodeContext<T extends WorkflowDataNode>(
    nodeId: string
  ): BaseNodeContext<T> {
    const nodeContext = this.globalNodeContextsByNodeId.get(nodeId);

    if (!nodeContext) {
      throw new NodeNotFoundError(`Failed to find node with id '${nodeId}'`);
    }

    return nodeContext as BaseNodeContext<T>;
  }

  public addPortContext(portContext: PortContext): void {
    const portId = portContext.portId;

    if (this.portContextById.get(portId)) {
      throw new NodePortGenerationError(
        `Port context already exists for port id: ${portId}`
      );
    }
    this.portContextById.set(portId, portContext);
  }

  public getPortContextById(portId: string): PortContext {
    const portContext: PortContext | undefined =
      this.portContextById.get(portId);

    if (!portContext) {
      throw new NodePortGenerationError(
        `Port context not found for port id: ${portId}`
      );
    }

    return portContext;
  }

  public async getMLModelNameById(mlModelId: string): Promise<string> {
    const mlModelName = this.mlModelNamesById[mlModelId];
    if (mlModelName) {
      return mlModelName;
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

  public addError(error: BaseCodegenError): void {
    if (this.strict) {
      throw error;
    }
    const errorExists = this.errors.some(
      (existingError) => existingError.message === error.message
    );

    if (!errorExists) {
      this.errors.push(error);
    }
  }

  public getErrors(): BaseCodegenError[] {
    return [...this.errors];
  }

  public isClassNameUsed(className: string): boolean {
    return this.classNames.has(className);
  }

  private addUsedClassName(className: string): void {
    this.classNames.add(className);
  }

  public getUniqueClassName(baseName: string): string {
    let sanitizedName = createPythonClassName(baseName);
    let numRenameAttempts = 0;

    if (!this.isClassNameUsed(sanitizedName)) {
      this.addUsedClassName(sanitizedName);
      return sanitizedName;
    }

    while (this.isClassNameUsed(sanitizedName)) {
      numRenameAttempts += 1;
      sanitizedName = `${createPythonClassName(baseName)}${numRenameAttempts}`;
    }

    this.addUsedClassName(sanitizedName);
    return sanitizedName;
  }
}
