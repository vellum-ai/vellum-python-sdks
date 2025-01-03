import { WorkflowContext } from "src/context";
import { PortContext } from "src/context/port-context";
import { NodeOutputNotFoundError } from "src/generators/errors";
import { WorkflowDataNode, WorkflowNodeDefinition } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";
import { getNodeId, getNodeLabel } from "src/utils/nodes";
import {
  getGeneratedNodeDisplayModulePath,
  getGeneratedNodeModuleInfo,
} from "src/utils/paths";

export declare namespace BaseNodeContext {
  interface Args<T extends WorkflowDataNode> {
    workflowContext: WorkflowContext;
    nodeData: T;
  }
}

export abstract class BaseNodeContext<T extends WorkflowDataNode> {
  protected workflowContext: WorkflowContext;
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

  constructor(args: BaseNodeContext.Args<T>) {
    this.workflowContext = args.workflowContext;
    this.nodeData = args.nodeData;

    this.baseNodeClassModulePath =
      this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH;
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

    const portContexts = this.createPortContexts();
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
  protected abstract createPortContexts(): PortContext[];

  public getNodeId(): string {
    return getNodeId(this.nodeData);
  }

  public getNodeLabel(): string {
    return getNodeLabel(this.nodeData);
  }

  public getNodeDefinition(): WorkflowNodeDefinition {
    return {
      name: this.nodeClassName,
      module: this.nodeModulePath,
      bases: [
        {
          name: this.baseNodeClassName,
          module: [
            ...(this.isCore
              ? this.workflowContext.sdkModulePathNames.CORE_NODES_MODULE_PATH
              : this.workflowContext.sdkModulePathNames
                  .DISPLAYABLE_NODES_MODULE_PATH),
          ],
        },
      ],
    };
  }

  public getNodeOutputNameById(outputId: string): string {
    // Lazily load node output names
    if (!this.nodeOutputNamesById) {
      this.nodeOutputNamesById = this.getNodeOutputNamesById();
    }

    const nodeOutputName = this.nodeOutputNamesById[outputId];

    if (!nodeOutputName) {
      throw new NodeOutputNotFoundError(
        `Failed to find output with id '${outputId}'`
      );
    }

    return toPythonSafeSnakeCase(nodeOutputName, "output");
  }
}
