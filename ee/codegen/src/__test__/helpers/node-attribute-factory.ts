import { NodeAttribute, WorkflowValueDescriptor } from "src/types/vellum";

export const nodeAttributeFactory = (
  id: string,
  name: string,
  value?: WorkflowValueDescriptor | null
): NodeAttribute => ({
  id,
  name,
  value,
});
