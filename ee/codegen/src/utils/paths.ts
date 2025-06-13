import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_INPUTS_MODULE_NAME,
  GENERATED_NODES_MODULE_NAME,
  GENERATED_STATE_MODULE_NAME,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { CodeResourceDefinition } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

export function getGeneratedInputsModulePath(
  workflowContext: WorkflowContext
): string[] {
  return [
    ...workflowContext.modulePath.slice(0, -1),
    GENERATED_INPUTS_MODULE_NAME,
  ];
}

export function getGeneratedStateModulePath(
  workflowContext: WorkflowContext
): string[] {
  return [
    ...workflowContext.modulePath.slice(0, -1),
    GENERATED_STATE_MODULE_NAME,
  ];
}

export function getGeneratedNodesModulePath(
  workflowContext: WorkflowContext
): string[] {
  if (workflowContext.parentNode) {
    if (workflowContext.nestedWorkflowModuleName) {
      return [
        ...workflowContext.parentNode.getNodeModulePath(),
        workflowContext.nestedWorkflowModuleName,
        GENERATED_NODES_MODULE_NAME,
      ];
    }
    return [
      ...workflowContext.parentNode.getNodeModulePath(),
      GENERATED_NODES_MODULE_NAME,
    ];
  } else {
    return [
      ...workflowContext.modulePath.slice(0, -1),
      GENERATED_NODES_MODULE_NAME,
    ];
  }
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

  // In the case of adorned Nodes, we need to traverse the Adornment Node's definition to get
  // info about the inner Node that it adorns.
  // TODO: Handle case where there's multiple adornments on the same Node
  //  https://app.shortcut.com/vellum/story/5699
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

  // Deduplicate the module name if it's already in use
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
  if (workflowContext.parentNode) {
    if (workflowContext.nestedWorkflowModuleName) {
      return [
        ...workflowContext.parentNode.getNodeDisplayModulePath(),
        workflowContext.nestedWorkflowModuleName,
        GENERATED_NODES_MODULE_NAME,
        moduleName,
      ];
    }
    return [
      ...workflowContext.parentNode.getNodeDisplayModulePath(),
      GENERATED_NODES_MODULE_NAME,
      moduleName,
    ];
  } else {
    return [
      ...workflowContext.modulePath.slice(0, -1),
      GENERATED_DISPLAY_MODULE_NAME,
      GENERATED_NODES_MODULE_NAME,
      moduleName,
    ];
  }
}

export function doesModulePathStartWith(
  modulePath?: readonly string[],
  prefix?: readonly string[]
): modulePath is string[] {
  if (!modulePath || !prefix) {
    return false;
  }

  return modulePath.join(".").startsWith(prefix.join("."));
}
