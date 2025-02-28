import { WorkflowContext } from "src/context";

export function workflowContextFactory({
  absolutePathToOutputDirectory,
  moduleName,
  workflowClassName,
  workflowRawData,
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
    workflowRawData: workflowRawData || {
      nodes: [],
      edges: [],
    },
    strict,
    codeExecutionNodeCodeRepresentationOverride,
    disableFormatting,
  });
}
