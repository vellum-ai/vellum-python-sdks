import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { ErrorNode } from "src/types/vellum";

export class ErrorNodeContext extends BaseNodeContext<ErrorNode> {
  baseNodeClassName = "ErrorNode";
  baseNodeDisplayClassName = "BaseErrorNodeDisplay";
  isCore = true;

  getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.errorOutputId]: "error",
    };
  }

  getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.errorOutputId]: "ERROR",
    };
  }

  createPortContexts(): PortContext[] {
    return [];
  }
}
