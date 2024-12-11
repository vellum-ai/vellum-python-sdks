import { terminalNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { FinalOutputNode as FinalOutputNodeType } from "src/types/vellum";

export function workflowOutputContextFactory({
  terminalNodeData,
}: {
  terminalNodeData?: FinalOutputNodeType;
} = {}): WorkflowOutputContext {
  return new WorkflowOutputContext({
    terminalNodeData: terminalNodeData ?? terminalNodeDataFactory(),
  });
}
