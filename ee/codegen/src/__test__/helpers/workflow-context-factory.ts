import { entrypointNodeDataFactory } from "./node-data-factories";

import { WorkflowContext } from "src/context";

export function workflowContextFactory({
  absolutePathToOutputDirectory,
  moduleName,
  workflowClassName,
  workflowRawData,
  strict = true,
}: Partial<WorkflowContext.Args> = {}): WorkflowContext {
  return new WorkflowContext({
    absolutePathToOutputDirectory:
      absolutePathToOutputDirectory || "./src/__tests__/",
    moduleName: moduleName || "code",
    workflowClassName: workflowClassName || "TestWorkflow",
    vellumApiKey: "<TEST_API_KEY>",
    workflowRawData: workflowRawData || {
      nodes: [entrypointNodeDataFactory()],
      edges: [],
    },
    strict,
  });
}
