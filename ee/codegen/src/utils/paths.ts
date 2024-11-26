import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_INPUTS_MODULE_NAME,
  GENERATED_NODES_MODULE_NAME,
} from "src/constants";
import { WorkflowContext } from "src/context";

export function getGeneratedInputsModulePath(
  workflowContext: WorkflowContext
): string[] {
  let modulePath: string[];
  if (workflowContext.parentNode) {
    modulePath = [
      ...workflowContext.parentNode.getNodeModulePath(),
      GENERATED_INPUTS_MODULE_NAME,
    ];
  } else {
    modulePath = [workflowContext.moduleName, GENERATED_INPUTS_MODULE_NAME];
  }

  return modulePath;
}

export function getGeneratedNodesModulePath(
  workflowContext: WorkflowContext
): string[] {
  let modulePath: string[];
  if (workflowContext.parentNode) {
    modulePath = [
      ...workflowContext.parentNode.getNodeModulePath(),
      GENERATED_NODES_MODULE_NAME,
    ];
  } else {
    modulePath = [workflowContext.moduleName, GENERATED_NODES_MODULE_NAME];
  }

  return modulePath;
}

export function getGeneratedNodeModulePath(
  workflowContext: WorkflowContext,
  moduleName: string
): string[] {
  return [...getGeneratedNodesModulePath(workflowContext), moduleName];
}

export function getGeneratedNodeDisplayModulePath(
  workflowContext: WorkflowContext,
  moduleName: string
): string[] {
  let modulePath: string[];
  if (workflowContext.parentNode) {
    modulePath = [
      ...workflowContext.parentNode.getNodeDisplayModulePath(),
      GENERATED_NODES_MODULE_NAME,
      moduleName,
    ];
  } else {
    modulePath = [
      workflowContext.moduleName,
      GENERATED_DISPLAY_MODULE_NAME,
      GENERATED_NODES_MODULE_NAME,
      moduleName,
    ];
  }

  return modulePath;
}
