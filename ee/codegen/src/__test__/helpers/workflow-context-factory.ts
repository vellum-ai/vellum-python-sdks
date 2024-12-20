import { WorkflowContext } from "src/context";

export function workflowContextFactory({
  absolutePathToOutputDirectory,
  moduleName,
  workflowClassName,
  workflowRawEdges,
}: Partial<WorkflowContext.Args> = {}): WorkflowContext {
  return new WorkflowContext({
    absolutePathToOutputDirectory:
      absolutePathToOutputDirectory || "./src/__tests__/",
    moduleName: moduleName || "code",
    workflowClassName: workflowClassName || "Workflow",
    vellumApiKey: "<TEST_API_KEY>",
    workflowRawEdges: workflowRawEdges || [],
    strict: true,
  });
}
