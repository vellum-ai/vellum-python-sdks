import { VellumVariable } from "vellum-ai/api/types";

export declare namespace OutputVariableContext {
  export type Args = {
    outputVariableData: VellumVariable;
  };
}

export class OutputVariableContext {
  private readonly outputVariableData: VellumVariable;
  public readonly name: string;

  constructor({ outputVariableData }: OutputVariableContext.Args) {
    this.outputVariableData = outputVariableData;
    this.name = outputVariableData.key;
  }

  public getOutputVariableId(): string {
    return this.outputVariableData.id;
  }

  public getOutputVariableData(): VellumVariable {
    return this.outputVariableData;
  }

  public getRawName(): string {
    return this.outputVariableData.key;
  }
}
