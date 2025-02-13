import { WorkflowContext } from "src/context";

export function workflowContextFactory({
  absolutePathToOutputDirectory,
  moduleName,
  workflowClassName,
  workflowRawEdges,
  codeExecutionNodeCodeRepresentationOverride = "STANDALONE",
  strict = true,
  disableFormatting = true,
}: Partial<WorkflowContext.Args> = {}): WorkflowContext {
  return new WorkflowContext({
    absolutePathToOutputDirectory:
      absolutePathToOutputDirectory || "./src/__tests__/",
    moduleName: moduleName || "code",
    workflowClassName: workflowClassName || "TestWorkflow",
    vellumApiKey: "<TEST_API_KEY>",
    workflowRawEdges: workflowRawEdges || [],
    strict,
    codeExecutionNodeCodeRepresentationOverride,
    disableFormatting,
  });
}
