import { NodeAttribute } from "src/types/vellum";

export const nodeAttributeFactory = (
  id: string,
  name: string,
  attributes: NodeAttribute[]
): NodeAttribute => ({
  id,
  name,
  value: {
    type: "CONSTANT_VALUE",
    value: {
      type: "JSON",
      value: attributes,
    },
  },
});
