import { isEmpty, isNil } from "lodash";

import { DEFAULT_PORT_NAME } from "src/constants";
import { WorkflowContext } from "src/context/index";
import { BaseNodeContext } from "src/context/node-context/base";
import { WorkflowDataNode } from "src/types/vellum";
import { toValidPythonIdentifier } from "src/utils/casing";

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
    this.portName = this.generateSanitizedPortName(portName);
    this.isDefault = isDefault;
  }

  public generateSanitizedPortName(portName: string): string {
    const defaultName = "port_";
    const rawPortName = portName;

    const initialPortName =
      !isNil(rawPortName) && !isEmpty(rawPortName)
        ? toValidPythonIdentifier(rawPortName, "port")
        : defaultName;

    // Deduplicate the port variable name if it's already in use
    let sanitizedName = initialPortName;
    let numRenameAttempts = 0;
    while (this.nodeContext.isPortNameUsed(sanitizedName)) {
      sanitizedName = `${initialPortName}${
        initialPortName.endsWith("_") ? "" : "_"
      }${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }

    this.nodeContext.addUsedPortName(sanitizedName);

    return sanitizedName;
  }
}
