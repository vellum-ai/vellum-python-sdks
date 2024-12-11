import { FinalOutputNode as FinalOutputNodeType } from "src/types/vellum";
import { toSnakeCase } from "src/utils/casing";

export declare namespace WorkflowOutputContext {
  export type Args = {
    terminalNodeData: FinalOutputNodeType;
  };
}

export class WorkflowOutputContext {
  private readonly terminalNodeData: FinalOutputNodeType;

  constructor({ terminalNodeData }: WorkflowOutputContext.Args) {
    this.terminalNodeData = terminalNodeData;
  }

  public getFinalOutputNodeId(): string {
    return this.terminalNodeData.id;
  }

  public getFinalOutputNodeData(): FinalOutputNodeType {
    return this.terminalNodeData;
  }

  public getOutputName(): string {
    return toSnakeCase(this.terminalNodeData.data.name);
  }
}
