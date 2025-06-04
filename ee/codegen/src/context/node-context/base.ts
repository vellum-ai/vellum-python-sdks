import { VellumVariableType } from "vellum-ai/api";

import {
  VELLUM_WORKFLOW_BASE_NODES_MODULE_PATH,
  VELLUM_WORKFLOW_NODES_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { PortContext } from "src/context/port-context";
import { NodeOutputNotFoundError } from "src/generators/errors";
import { NodePort as NodePortType, WorkflowDataNode } from "src/types/vellum";
import { toPythonSafeSnakeCaseWithCasePreservation } from "src/utils/casing";
import { getNodeLabel } from "src/utils/nodes";
import {
  doesModulePathStartWith,
  getGeneratedNodeDisplayModulePath,
  getGeneratedNodeModuleInfo,
} from "src/utils/paths";
import { hasErrorOutput } from "src/utils/typing";

export declare namespace BaseNodeContext {
  interface Args<T extends WorkflowDataNode> {
    workflowContext: WorkflowContext;
    nodeData: T;
    importOrder: readonly number[];
  }
}

export abstract class BaseNodeContext<T extends WorkflowDataNode> {
  public readonly workflowContext: WorkflowContext;
  public readonly importOrder: readonly number[];
  public readonly nodeModulePath: string[];
  public readonly nodeModuleName: string;
  public readonly nodeFileName: string;
  public readonly nodeClassName: string;
  public readonly nodeDisplayModulePath: string[];
  public readonly nodeDisplayModuleName: string;
  public readonly nodeDisplayFileName: string;
  public readonly nodeDisplayClassName: string;

  public nodeData: T;
  public abstract readonly baseNodeClassName: string;
  public abstract readonly baseNodeDisplayClassName: string;

  protected isCore = false;
  public readonly baseNodeClassModulePath: readonly string[];
  public readonly baseNodeDisplayClassModulePath: readonly string[];

  private nodeOutputNamesById: Record<string, string> | undefined;
  public readonly portContextsById: Map<string, PortContext>;
  public readonly defaultPortContext: PortContext | undefined;

  private readonly nodePortNames: Set<string> = new Set();

  constructor(args: BaseNodeContext.Args<T>) {
    this.workflowContext = args.workflowContext;
    this.nodeData = args.nodeData;
    this.importOrder = args.importOrder;

    if (args.nodeData.type === "GENERIC") {
      if (
        !doesModulePathStartWith(
          args.nodeData.base?.module,
          VELLUM_WORKFLOW_BASE_NODES_MODULE_PATH
        )
      ) {
        this.baseNodeClassModulePath = args.nodeData.base.module;
      } else {
        this.baseNodeClassModulePath = VELLUM_WORKFLOW_NODES_MODULE_PATH;
      }
    } else if (
      !doesModulePathStartWith(
        args.nodeData.base?.module,
        VELLUM_WORKFLOW_NODES_MODULE_PATH
      )
    ) {
      this.baseNodeClassModulePath =
        args.nodeData.base?.module ??
        this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH;
    } else {
      this.baseNodeClassModulePath =
        this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH;
    }
    this.baseNodeDisplayClassModulePath =
      this.workflowContext.sdkModulePathNames.NODE_DISPLAY_MODULE_PATH;

    const { moduleName, nodeClassName, modulePath } =
      getGeneratedNodeModuleInfo({
        workflowContext: args.workflowContext,
        nodeDefinition: args.nodeData.definition,
        nodeLabel: this.getNodeLabel(),
      });
    this.nodeModuleName = moduleName;
    this.nodeClassName = nodeClassName;
    this.nodeModulePath = modulePath;
    this.nodeFileName = `${this.nodeModuleName}.py`;

    this.nodeDisplayModuleName = this.nodeModuleName;
    this.nodeDisplayFileName = `${this.nodeDisplayModuleName}.py`;
    this.nodeDisplayClassName = `${this.nodeClassName}Display`;
    this.nodeDisplayModulePath = getGeneratedNodeDisplayModulePath(
      args.workflowContext,
      this.nodeDisplayModuleName
    );

    const portContexts = this.nodeData.ports
      ? this.createPortContextsFromNodePortAttribute(this.nodeData.ports)
      : this.createPortContexts();
    portContexts.forEach((portContext) => {
      this.workflowContext.addPortContext(portContext);
    });

    this.portContextsById = new Map(
      portContexts.map((portContext) => [portContext.portId, portContext])
    );

    this.defaultPortContext = portContexts.find(
      (portContext) => portContext.isDefault
    );
  }

  protected abstract getNodeOutputNamesById(): Record<string, string>;
  protected abstract getNodeOutputTypesById(): Record<
    string,
    VellumVariableType
  >;
  protected abstract createPortContexts(): PortContext[];

  protected createPortContextsFromNodePortAttribute(
    nodePorts: NodePortType[]
  ): PortContext[] {
    return nodePorts.map(
      (port) =>
        new PortContext({
          workflowContext: this.workflowContext,
          nodeContext: this,
          portId: port.id,
          portName: port.name,
          isDefault: port.type === "DEFAULT",
        })
    );
  }

  public getNodeLabel(): string {
    return getNodeLabel(this.nodeData);
  }

  public getNodeOutputNameById(outputId: string): string | undefined {
    // Lazily load node output names
    if (!this.nodeOutputNamesById) {
      this.nodeOutputNamesById = this.getNodeOutputNamesById();
    }

    const nodeOutputName = this.nodeOutputNamesById[outputId];
    if (!nodeOutputName) {
      // This handles an edge case where the node references a non-existent subworkflow deployment
      if (
        this.nodeData.type === "SUBWORKFLOW" &&
        this.nodeData.data.variant === "DEPLOYMENT"
      ) {
        this.workflowContext.addError(
          new NodeOutputNotFoundError(
            `Could not find Subworkflow Deployment Output with id ${outputId}`,
            "WARNING"
          )
        );
        return;
      }

      throw new NodeOutputNotFoundError(
        `Failed to find ${this.nodeClassName} Output with id '${outputId}'`,
        "WARNING"
      );
    }

    return toPythonSafeSnakeCaseWithCasePreservation(nodeOutputName, "output");
  }

  public getNodeOutputTypeById(
    outputId: string
  ): VellumVariableType | undefined {
    const nodeOutputTypesById = this.getNodeOutputTypesById();

    return nodeOutputTypesById[outputId];
  }

  public isPortNameUsed(portName: string): boolean {
    return this.nodePortNames.has(portName);
  }

  public addUsedPortName(portName: string): void {
    this.nodePortNames.add(portName);
  }

  /**
   * Extend this class to perform any additional property generation asynchronously
   * after the node context has been created.
   */
  public buildProperties(): Promise<void> {
    return Promise.resolve();
  }

  public isImportedBefore(
    nodeContext: BaseNodeContext<WorkflowDataNode>
  ): boolean {
    for (
      let i = 0;
      i < Math.max(this.importOrder.length, nodeContext.importOrder.length);
      i++
    ) {
      const thisImportOrder = this.importOrder[i];
      const otherImportOrder = nodeContext.importOrder[i];
      if (thisImportOrder === undefined && otherImportOrder === undefined) {
        return false;
      }

      if (thisImportOrder === undefined) {
        return true;
      }

      if (otherImportOrder === undefined) {
        return false;
      }

      if (thisImportOrder < otherImportOrder) {
        return true;
      }

      if (thisImportOrder > otherImportOrder) {
        return false;
      }
    }
    return false;
  }

  protected getErrorOutputId(): string | undefined {
    const TRY_NODE_NAME = "TryNode";
    const tryNodes = this.nodeData.adornments?.filter((adornment) => {
      return adornment.base.name === TRY_NODE_NAME;
    });

    const tryNode = tryNodes?.at(-1);

    let fallbackErrorOutputId: string | undefined = undefined;
    if (hasErrorOutput(this.nodeData)) {
      fallbackErrorOutputId = this.nodeData.data.errorOutputId;
    }

    return tryNode ? tryNode.id : fallbackErrorOutputId;
  }
}
