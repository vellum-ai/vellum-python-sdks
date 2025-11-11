import nodeDefinitions from "src/assets/node-definitions.json";

export type NodeDefinition = (typeof nodeDefinitions.nodes)[number];

export function findNodeDefinitionByBaseClassName(
  baseClassName: string
): NodeDefinition | undefined {
  return nodeDefinitions.nodes.find(
    (node) => node.definition?.name === baseClassName
  );
}
