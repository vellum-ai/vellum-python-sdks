import {
  ErrorLogFile,
  InitFile,
  Inputs,
  NodeInput,
  VellumValue,
  VellumVariable,
  Workflow,
} from "./generators";
import { BasePersistedFile } from "./generators/base-persisted-file";
import { State } from "./generators/state";
import { WorkflowSandboxFile } from "./generators/workflow-sandbox-file";

export function vellumVariable(args: VellumVariable.Args): VellumVariable {
  return new VellumVariable(args);
}

export function vellumValue(args: VellumValue.Args): VellumValue {
  return new VellumValue(args);
}

export function nodeInput(args: NodeInput.Args): NodeInput {
  return new NodeInput(args);
}

export function inputs(args: Inputs.Args): Inputs {
  return new Inputs(args);
}

export function state(args: State.Args): State {
  return new State(args);
}

export function workflow(args: Workflow.Args): Workflow {
  return new Workflow(args);
}

export function initFile(args: InitFile.Args): InitFile {
  return new InitFile(args);
}

export function errorLogFile(args: BasePersistedFile.Args): ErrorLogFile {
  return new ErrorLogFile(args);
}

export function workflowSandboxFile(
  args: WorkflowSandboxFile.Args
): WorkflowSandboxFile {
  return new WorkflowSandboxFile(args);
}
