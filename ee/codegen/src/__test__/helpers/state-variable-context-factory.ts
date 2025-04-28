import { VellumVariable } from "vellum-ai/api/types";

import { WorkflowContext } from "src/context";
import { StateVariableContext } from "src/context/state-variable-context";

export function stateVariableContextFactory({
  stateVariableData,
  workflowContext,
}: {
  stateVariableData: VellumVariable;
  workflowContext: WorkflowContext;
}): StateVariableContext {
  return new StateVariableContext({
    stateVariableData,
    workflowContext,
  });
}
