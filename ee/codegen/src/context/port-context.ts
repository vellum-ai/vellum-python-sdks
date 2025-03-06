import { DEFAULT_PORT_NAME } from "src/constants";
import { WorkflowContext } from "src/context/index";
import { BaseNodeContext } from "src/context/node-context/base";
import { WorkflowDataNode } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

export declare namespace PortContext {
  export type Args = {
    workflowContext: WorkflowContext;
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    // portId should be set to the value of sourceHandleId;
    portId: string;
    portName?: string;
    isDefault?: boolean;
  };
}

export class PortContext {
  public readonly workflowContext: WorkflowContext;
  public readonly nodeContext: BaseNodeContext<WorkflowDataNode>;
  public readonly portId: string;
  public readonly portName: string;
  public readonly isDefault: boolean;

  constructor({
    workflowContext,
    nodeContext,
    portId,
    portName = DEFAULT_PORT_NAME,
    isDefault = true,
  }: PortContext.Args) {
    this.workflowContext = workflowContext;
    this.nodeContext = nodeContext;

    this.portId = portId;
    this.portName = toPythonSafeSnakeCase(portName);
    this.isDefault = isDefault;
  }
}
