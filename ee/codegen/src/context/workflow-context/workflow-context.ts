import { join } from "path";

import { VellumEnvironmentUrls } from "vellum-ai";
import { CodeResourceDefinition, WorkspaceSecretRead } from "vellum-ai/api";
import { MlModels } from "vellum-ai/api/resources/mlModels/client/Client";
import { WorkspaceSecrets as WorkspaceSecretsClient } from "vellum-ai/api/resources/workspaceSecrets/client/Client";

import { GENERATED_WORKFLOW_MODULE_NAME } from "src/constants";
import { InputVariableContext } from "src/context/input-variable-context";
import { BaseNodeContext } from "src/context/node-context/base";
import { OutputVariableContext } from "src/context/output-variable-context";
import { PortContext } from "src/context/port-context";
import { StateVariableContext } from "src/context/state-variable-context";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { generateSdkModulePaths } from "src/context/workflow-context/sdk-module-paths";
import { SDK_MODULE_PATHS } from "src/context/workflow-context/types";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import {
  BaseCodegenError,
  CodegenErrorSeverity,
  NodeDefinitionGenerationError,
  NodeNotFoundError,
  NodePortGenerationError,
  NodePortNotFoundError,
  WorkflowGenerationError,
  WorkflowInputGenerationError,
  WorkflowOutputGenerationError,
} from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases";
import {
  EntrypointNode,
  WorkflowDataNode,
  WorkflowEdge,
  WorkflowRawData,
  WorkflowTrigger,
} from "src/types/vellum";
import { createPythonClassName } from "src/utils/casing";

type InputVariableContextsById = Map<string, InputVariableContext>;

type StateVariableContextsById = Map<string, StateVariableContext>;

type OutputVariableContextsById = Map<string, OutputVariableContext>;

type NodeContextsByNodeId = Map<string, BaseNodeContext<WorkflowDataNode>>;

type TriggerContextsByTriggerId = Map<
  string,
  BaseTriggerContext<WorkflowTrigger>
>;

// A mapping between source handle ids and port contexts
type PortContextById = Map<string, PortContext>;

export declare namespace WorkflowContext {
  export type Args = {
    absolutePathToOutputDirectory: string;
    moduleName: string;
    workflowClassName: string;
    globalInputVariableContextsById?: InputVariableContextsById;
    globalStateVariableContextsById?: StateVariableContextsById;
    globalNodeContextsByNodeId?: NodeContextsByNodeId;
    globalOutputVariableContextsById?: OutputVariableContextsById;
    pythonCodeMergeableNodeFiles?: Set<string>;
    parentNode?: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowsSdkModulePath?: readonly string[];
    portContextByName?: PortContextById;
    vellumApiKey: string;
    vellumApiEnvironment?: VellumEnvironmentUrls;
    workflowRawData: WorkflowRawData;
    inputsClassDefinition?: CodeResourceDefinition;
    strict: boolean;
    classNames?: Set<string>;
    nestedWorkflowModuleName?: string;
    workflowClassDescription?: string;
    triggers?: WorkflowTrigger[];
  };
}

export class WorkflowContext {
  public readonly absolutePathToOutputDirectory: string;
  public readonly modulePath: string[];
  public readonly moduleName: string;
  public readonly label: string | undefined;
  public readonly workflowClassName: string;
  public readonly workflowClassDescription?: string;

  // Maps workflow input variable IDs to the input variable
  // Tracks local and global contexts in the case of nested workflows.
  public readonly inputVariableContextsById: InputVariableContextsById;
  public readonly globalInputVariableContextsById: InputVariableContextsById;

  // Maps workflow state variable IDs to the state variable
  // Tracks local and global contexts in the case of nested workflows.
  public readonly stateVariableContextsById: StateVariableContextsById;
  public readonly globalStateVariableContextsById: StateVariableContextsById;

  // Maps workflow output variable IDs to the output variable
  // Tracks local and global contexts in the case of nested workflows.
  public readonly outputVariableContextsById: OutputVariableContextsById;
  public readonly globalOutputVariableContextsById: OutputVariableContextsById;

  public readonly strict: boolean;

  // Track what input variables names are used within this workflow so that we can ensure name uniqueness when adding
  // new input variables.
  private readonly inputVariableNames: Set<string> = new Set();

  // Track what state variables names are used within this workflow so that we can ensure name uniqueness when adding
  // new state variables.
  private readonly stateVariableNames: Set<string> = new Set();

  // Maps node IDs to a mapping of output IDs to output names.
  // Tracks local and global contexts in the case of nested workflows.
  public readonly nodeContextsByNodeId: NodeContextsByNodeId;
  public readonly globalNodeContextsByNodeId: NodeContextsByNodeId;

  // Track what node module names are used within this workflow so that we can ensure name uniqueness when adding
  // new nodes.
  private readonly nodeModuleNames: Set<string> = new Set();

  // Maps trigger IDs to trigger contexts
  // Tracks local and global contexts in the case of nested workflows.
  public readonly triggerContextsByTriggerId: TriggerContextsByTriggerId;
  public readonly globalTriggerContextsByTriggerId: TriggerContextsByTriggerId;

  // Track the custom workflow module name if it exists
  public readonly nestedWorkflowModuleName?: string;

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
  public readonly vellumApiEnvironment?: VellumEnvironmentUrls;
  private readonly mlModelNamesById: Record<string, string> = {};
  private readonly errors: BaseCodegenError[] = [];

  // Track node files that will be merged by codegen-service
  private readonly pythonCodeMergeableNodeFiles: Set<string>;

  public readonly workflowRawData: WorkflowRawData;

  // Track what class names are used within this workflow so that we can ensure name uniqueness
  public readonly classNames: Set<string>;

  // Track Vellum entities that have been loaded
  private readonly loadedWorkspaceSecretsById: Record<
    string,
    WorkspaceSecretRead
  > = {};

  public readonly triggers?: WorkflowTrigger[];

  constructor({
    absolutePathToOutputDirectory,
    moduleName,
    workflowClassName,
    workflowClassDescription,
    globalInputVariableContextsById,
    globalStateVariableContextsById,
    globalNodeContextsByNodeId,
    globalOutputVariableContextsById,
    parentNode,
    workflowsSdkModulePath = ["vellum", "workflows"] as const,
    portContextByName,
    vellumApiKey,
    vellumApiEnvironment,
    workflowRawData,
    strict,
    classNames,
    nestedWorkflowModuleName,
    pythonCodeMergeableNodeFiles,
    triggers,
  }: WorkflowContext.Args) {
    this.absolutePathToOutputDirectory = absolutePathToOutputDirectory;
    this.moduleName = moduleName;
    this.nestedWorkflowModuleName = nestedWorkflowModuleName;

    if (parentNode) {
      if (nestedWorkflowModuleName) {
        this.modulePath = [
          ...parentNode.nodeContext.nodeModulePath,
          nestedWorkflowModuleName,
          GENERATED_WORKFLOW_MODULE_NAME,
        ];
      } else {
        this.modulePath = [
          ...parentNode.nodeContext.nodeModulePath,
          GENERATED_WORKFLOW_MODULE_NAME,
        ];
      }
    } else {
      this.modulePath = [
        ...this.moduleName.split("."),
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    }

    this.workflowClassName = workflowClassName;
    this.workflowClassDescription = workflowClassDescription;
    this.vellumApiKey = vellumApiKey;
    this.vellumApiEnvironment = vellumApiEnvironment;

    this.inputVariableContextsById = new Map();
    this.globalInputVariableContextsById =
      globalInputVariableContextsById ?? new Map();

    this.stateVariableContextsById = new Map();
    this.globalStateVariableContextsById =
      globalStateVariableContextsById ?? new Map();

    this.nodeContextsByNodeId = new Map();
    this.globalNodeContextsByNodeId = globalNodeContextsByNodeId ?? new Map();

    this.triggerContextsByTriggerId = new Map();
    this.globalTriggerContextsByTriggerId = new Map();

    this.portContextById = portContextByName ?? new Map();

    this.parentNode = parentNode;

    this.sdkModulePathNames = generateSdkModulePaths(workflowsSdkModulePath);
    this.workflowRawData = workflowRawData;
    this.triggers = triggers;

    this.strict = strict;
    this.errors = [];

    this.outputVariableContextsById = new Map();
    this.globalOutputVariableContextsById =
      globalOutputVariableContextsById ?? new Map();

    this.classNames = classNames ?? new Set<string>();

    this.pythonCodeMergeableNodeFiles =
      pythonCodeMergeableNodeFiles ?? new Set<string>();
  }

  public getAbsolutePath(filePath: string): string {
    return join(
      this.absolutePathToOutputDirectory,
      ...this.modulePath.slice(0, -1),
      filePath
    );
  }

  /* Create a new workflow context for a nested workflow from its parent */
  public createNestedWorkflowContext({
    parentNode,
    workflowClassName,
    workflowRawData,
    classNames,
    nestedWorkflowModuleName,
    workflowClassDescription,
  }: {
    parentNode: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;
    workflowClassName: string;
    workflowRawData: WorkflowRawData;
    classNames?: Set<string>;
    nestedWorkflowModuleName?: string;
    workflowClassDescription?: string;
  }) {
    return new WorkflowContext({
      absolutePathToOutputDirectory: this.absolutePathToOutputDirectory,
      moduleName: this.moduleName,
      workflowClassName: workflowClassName,
      globalInputVariableContextsById: this.globalInputVariableContextsById,
      globalStateVariableContextsById: this.globalStateVariableContextsById,
      globalNodeContextsByNodeId: this.globalNodeContextsByNodeId,
      globalOutputVariableContextsById: this.globalOutputVariableContextsById,
      pythonCodeMergeableNodeFiles: this.pythonCodeMergeableNodeFiles,
      parentNode,
      workflowsSdkModulePath: this.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      vellumApiKey: this.vellumApiKey,
      vellumApiEnvironment: this.vellumApiEnvironment,
      workflowRawData,
      strict: this.strict,
      classNames,
      nestedWorkflowModuleName,
      workflowClassDescription,
    });
  }

  public tryGetEntrypointNode(): EntrypointNode | null {
    if (this.entrypointNode) {
      return this.entrypointNode;
    }

    const entrypointNodes = this.workflowRawData.nodes.filter(
      (n): n is EntrypointNode => n.type === "ENTRYPOINT"
    );
    if (entrypointNodes.length > 1) {
      throw new WorkflowGenerationError("Multiple entrypoint nodes found");
    }

    const entrypointNode = entrypointNodes[0];
    if (!entrypointNode) {
      return null;
    }
    this.entrypointNode = entrypointNode;

    return this.entrypointNode;
  }

  public getTriggerEdges(): WorkflowEdge[] {
    // First, check if we have triggers and edges from those triggers
    const triggerIds = new Set((this.triggers ?? []).map((t) => t.id));

    // Fall back to ENTRYPOINT node for backward compatibility
    const entrypointNode = this.tryGetEntrypointNode();
    if (entrypointNode) {
      triggerIds.add(entrypointNode.id);
    }

    return this.workflowRawData.edges.filter((edge) =>
      triggerIds.has(edge.sourceNodeId)
    );
  }

  public getEdgesByPortId(): Map<string, WorkflowEdge[]> {
    const edgesByPortId = new Map<string, WorkflowEdge[]>();
    this.workflowRawData.edges.forEach((edge) => {
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

  public isStateVariableNameUsed(stateVariableName: string): boolean {
    return this.stateVariableNames.has(stateVariableName);
  }

  private addUsedStateVariableName(stateVariableName: string) {
    this.stateVariableNames.add(stateVariableName);
  }

  public addStateVariableContext(
    stateVariableContext: StateVariableContext
  ): void {
    const stateVariableId = stateVariableContext.getStateVariableId();
    if (this.globalStateVariableContextsById.get(stateVariableId)) {
      throw new WorkflowInputGenerationError(
        `State variable context already exists for state variable ID: ${stateVariableId}`
      );
    }

    this.stateVariableContextsById.set(stateVariableId, stateVariableContext);
    this.globalStateVariableContextsById.set(
      stateVariableId,
      stateVariableContext
    );
    this.addUsedStateVariableName(stateVariableContext.name);
  }

  public findInputVariableContextById(
    inputVariableId: string
  ): InputVariableContext | undefined {
    return this.globalInputVariableContextsById.get(inputVariableId);
  }

  public findStateVariableContextById(
    stateVariableId: string
  ): StateVariableContext | undefined {
    return this.globalStateVariableContextsById.get(stateVariableId);
  }

  public findOutputVariableContextById(
    outputVariableId: string
  ): OutputVariableContext | undefined {
    return this.globalOutputVariableContextsById.get(outputVariableId);
  }

  public addOutputVariableContext(
    outputVariableContext: OutputVariableContext
  ): void {
    const outputVariableId = outputVariableContext.getOutputVariableId();

    if (this.globalOutputVariableContextsById.get(outputVariableId)) {
      this.addError(
        new WorkflowOutputGenerationError(
          `Output variable context already exists for output variable ID: ${outputVariableId}`,
          "WARNING"
        )
      );
      return;
    }

    this.outputVariableContextsById.set(
      outputVariableId,
      outputVariableContext
    );
    this.globalOutputVariableContextsById.set(
      outputVariableId,
      outputVariableContext
    );

    // This was added from the workflow output context. We should remove this once terminal node data is removed from data
    this.addUsedOutputVariableName(outputVariableContext.name);
  }

  public getOutputVariableContextById(
    outputVariableId: string
  ): OutputVariableContext | undefined {
    const outputVariableContext =
      this.findOutputVariableContextById(outputVariableId);

    if (!outputVariableContext) {
      this.addError(
        new WorkflowOutputGenerationError(
          `Output variable context not found for ID: ${outputVariableId}`,
          "WARNING"
        )
      );
      return undefined;
    }

    return outputVariableContext;
  }

  public findInputVariableContextByRawName(
    rawName: string
  ): InputVariableContext | undefined {
    return Array.from(this.inputVariableContextsById.values()).find(
      (inputContext) => inputContext.getRawName() === rawName
    );
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
      this.addError(
        new NodeDefinitionGenerationError(
          `Node context already exists for node ID: ${nodeId}`,
          "WARNING"
        )
      );
      return;
    }

    this.nodeContextsByNodeId.set(nodeId, nodeContext);
    this.globalNodeContextsByNodeId.set(nodeId, nodeContext);
    this.addUsedNodeModuleName(nodeContext.nodeModuleName);
  }

  public findNodeContext(
    nodeId: string
  ): BaseNodeContext<WorkflowDataNode> | undefined {
    const nodeContext = this.globalNodeContextsByNodeId.get(nodeId);

    if (!nodeContext) {
      this.addError(
        new NodeNotFoundError(
          `Failed to find node with id '${nodeId}'`,
          "WARNING"
        )
      );
    }

    return nodeContext;
  }

  public findLocalNodeContext(
    nodeId: string
  ): BaseNodeContext<WorkflowDataNode> | undefined {
    const nodeContext = this.nodeContextsByNodeId.get(nodeId);
    if (!nodeContext) {
      this.addError(
        new NodeNotFoundError(
          `Failed to find Node with id '${nodeId}' in the current Workflow`,
          "WARNING"
        )
      );
      return undefined;
    }

    return nodeContext;
  }

  public addTriggerContext(
    triggerContext: BaseTriggerContext<WorkflowTrigger>
  ): void {
    const triggerId = triggerContext.getTriggerId();

    if (this.globalTriggerContextsByTriggerId.get(triggerId)) {
      this.addError(
        new WorkflowGenerationError(
          `Trigger context already exists for trigger ID: ${triggerId}`,
          "WARNING"
        )
      );
      return;
    }

    this.triggerContextsByTriggerId.set(triggerId, triggerContext);
    this.globalTriggerContextsByTriggerId.set(triggerId, triggerContext);
  }

  public findTriggerContext(
    triggerId: string
  ): BaseTriggerContext<WorkflowTrigger> | undefined {
    return this.globalTriggerContextsByTriggerId.get(triggerId);
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
      throw new NodePortNotFoundError(
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

    const mlModel = await new MlModels({
      apiKey: this.vellumApiKey,
      environment: this.vellumApiEnvironment,
    }).retrieve(mlModelId);

    this.mlModelNamesById[mlModelId] = mlModel.name;
    return mlModel.name;
  }

  public addError(error: BaseCodegenError): void {
    if (this.strict) {
      throw error;
    } else {
      error.log();
    }

    const errorExists = this.errors.some(
      (existingError) => existingError.message === error.message
    );

    if (!errorExists) {
      this.errors.push(error);
    }
  }

  public getErrors(severity?: CodegenErrorSeverity): BaseCodegenError[] {
    const allErrors = [...this.errors];
    if (!severity) {
      return allErrors;
    }
    return allErrors.filter((error) => error.severity === severity);
  }

  public isClassNameUsed(className: string): boolean {
    return this.classNames.has(className);
  }

  public addUsedClassName(className: string): void {
    this.classNames.add(className);
  }

  public getUniqueClassName(baseName: string): string {
    let sanitizedName = createPythonClassName(baseName);
    let numRenameAttempts = 0;

    if (!this.isClassNameUsed(sanitizedName)) {
      return sanitizedName;
    }

    while (this.isClassNameUsed(sanitizedName)) {
      numRenameAttempts += 1;
      sanitizedName = `${createPythonClassName(baseName)}${numRenameAttempts}`;
    }

    return sanitizedName;
  }

  /**
   * Adds a file path to the set of node files that need to be merged by codegen-service
   * @param filePath Path to the node file
   */
  public addPythonCodeMergeableNodeFile(filePath: string): void {
    this.pythonCodeMergeableNodeFiles.add(filePath);
  }

  /**
   * Gets the set of node file paths that will be merged by codegen-service
   * @returns Set of node file paths
   */
  public getPythonCodeMergeableNodeFiles(): Set<string> {
    return this.pythonCodeMergeableNodeFiles;
  }

  public async loadWorkspaceSecret(workspaceSecretId: string): Promise<void> {
    if (this.loadedWorkspaceSecretsById[workspaceSecretId]) {
      return;
    }

    const workspaceSecret = await new WorkspaceSecretsClient({
      apiKey: this.vellumApiKey,
      environment: this.vellumApiEnvironment,
    }).retrieve(workspaceSecretId);
    this.loadedWorkspaceSecretsById[workspaceSecretId] = workspaceSecret;
  }

  public getWorkspaceSecretName(workspaceSecretId: string): string {
    return (
      this.loadedWorkspaceSecretsById[workspaceSecretId]?.name ??
      workspaceSecretId
    );
  }

  public getRootModulePath(): string[] {
    if (this.parentNode) {
      return this.parentNode.workflowContext.getRootModulePath();
    }
    return this.modulePath;
  }
}
