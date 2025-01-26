import { WorkflowContext } from "src/context";

export function workflowContextFactory(
  {
    absolutePathToOutputDirectory,
    moduleName,
    workflowClassName,
    workflowRawEdges,
    codeExecutionNodeCodeRepresentationOverride,
    strict = true,
  }: Partial<WorkflowContext.Args> = {
    codeExecutionNodeCodeRepresentationOverride: "STANDALONE",
  }
): WorkflowContext {
  return new WorkflowContext({
    absolutePathToOutputDirectory:
      absolutePathToOutputDirectory || "./src/__tests__/",
    moduleName: moduleName || "code",
    workflowClassName: workflowClassName || "TestWorkflow",
    vellumApiKey: "<TEST_API_KEY>",
    workflowRawEdges: workflowRawEdges || [],
    strict,
    codeExecutionNodeCodeRepresentationOverride,
  });
}
