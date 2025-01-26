import { entrypointNodeDataFactory } from "./node-data-factories";

import { WorkflowContext } from "src/context";

export function workflowContextFactory(
  {
    absolutePathToOutputDirectory,
    moduleName,
    workflowClassName,
    workflowRawNodes,
    workflowRawEdges,
    codeExecutionNodeCodeRepresentationOverride,
    strict = true,
  }: Partial<WorkflowContext.Args> = {
    codeExecutionNodeCodeRepresentationOverride: "STANDALONE",
  }
): WorkflowContext {
  const nodes = workflowRawNodes || [entrypointNodeDataFactory()];

  return new WorkflowContext({
    absolutePathToOutputDirectory:
      absolutePathToOutputDirectory || "./src/__tests__/",
    moduleName: moduleName || "code",
    workflowClassName: workflowClassName || "TestWorkflow",
    vellumApiKey: "<TEST_API_KEY>",
    workflowRawNodes: nodes,
    workflowRawEdges: workflowRawEdges || [],
    strict,
    codeExecutionNodeCodeRepresentationOverride,
  });
}
