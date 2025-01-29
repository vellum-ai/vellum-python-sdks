import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_INPUTS_MODULE_NAME,
  GENERATED_NODES_MODULE_NAME,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { CodeResourceDefinition } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

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

export function getGeneratedNodeModuleInfo({
  workflowContext,
  nodeDefinition,
  nodeLabel,
}: {
  workflowContext: WorkflowContext;
  nodeDefinition: CodeResourceDefinition | undefined;
  nodeLabel: string;
}): { moduleName: string; nodeClassName: string; modulePath: string[] } {
  const modulePathLeaf =
    nodeDefinition?.module?.[nodeDefinition.module.length - 1];

  let rawModuleName: string;
  let nodeClassName: string;

  if (modulePathLeaf && modulePathLeaf === "<adornment>") {
    rawModuleName =
      nodeDefinition?.module?.[nodeDefinition.module.length - 3] ??
      toPythonSafeSnakeCase(nodeLabel, "node");

    nodeClassName =
      nodeDefinition?.module?.[nodeDefinition.module.length - 2] ??
      workflowContext.getUniqueClassName(nodeLabel);
  } else {
    rawModuleName = modulePathLeaf ?? toPythonSafeSnakeCase(nodeLabel, "node");

    nodeClassName =
      nodeDefinition?.name ?? workflowContext.getUniqueClassName(nodeLabel);
  }

  let moduleName = rawModuleName;
  let numRenameAttempts = 0;
  while (workflowContext.isNodeModuleNameUsed(moduleName)) {
    moduleName = `${rawModuleName}_${numRenameAttempts + 1}`;
    numRenameAttempts += 1;
  }

  const modulePath = [
    ...getGeneratedNodesModulePath(workflowContext),
    moduleName,
  ];
  return { moduleName, nodeClassName, modulePath };
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
