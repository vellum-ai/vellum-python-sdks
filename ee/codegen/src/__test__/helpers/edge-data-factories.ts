import { WorkflowEdge, WorkflowNode } from "src/types/vellum";

const getSourceHandleId = (
  node: WorkflowNode | [WorkflowNode, string]
): string => {
  if (Array.isArray(node)) {
    const [actualNode, portName] = node;

    if (actualNode.type === "GENERIC") {
      const id = actualNode.ports.find((port) => port.name === portName)?.id;
      if (!id) {
        throw new Error(`Port not found: ${portName}`);
      }

      return id;
    }

    if (actualNode.type === "CONDITIONAL") {
      const id = actualNode.data.conditions[Number(portName)]?.sourceHandleId;
      if (!id) {
        throw new Error("Conditional node has no source handle id");
      }

      return id;
    }

    return getSourceHandleId(actualNode);
  }

  if (node.type === "GENERIC") {
    const port = node.ports[0];
    if (!port) {
      throw new Error("Generic node has no ports");
    }

    return port.id;
  }

  if (
    node.type == "TERMINAL" ||
    node.type === "NOTE" ||
    node.type === "ERROR"
  ) {
    throw new Error(`${node.type} nodes have no source handle id`);
  }

  if (node.type === "CONDITIONAL") {
    throw new Error("Conditional nodes must include a port name");
  }

  return node.data.sourceHandleId;
};

const getTargetHandleId = (
  node: WorkflowNode | [WorkflowNode, number]
): string => {
  if (Array.isArray(node)) {
    const [actualNode, targetIndex] = node;
    if (actualNode.type === "MERGE") {
      const id = actualNode.data.targetHandles[targetIndex]?.id;
      if (!id) {
        throw new Error(`Target handle not found: ${targetIndex}`);
      }

      return id;
    }

    return getTargetHandleId(actualNode);
  }

  if (node.type === "GENERIC") {
    return node.trigger.id;
  }

  if (node.type === "MERGE") {
    throw new Error("Merge nodes must include target handle index");
  }

  if (node.type === "ENTRYPOINT" || node.type === "NOTE") {
    throw new Error(`${node.type} nodes have no target handle id`);
  }

  return node.data.targetHandleId;
};

export type EdgeFactoryNodePair = [
  WorkflowNode | [WorkflowNode, string],
  WorkflowNode | [WorkflowNode, number]
];

export function edgesFactory(nodePairs: EdgeFactoryNodePair[]): WorkflowEdge[] {
  return nodePairs.map(([sourceNode, targetNode], index) => ({
    id: `edge-${index + 1}`,
    type: "DEFAULT",
    sourceNodeId: Array.isArray(sourceNode) ? sourceNode[0].id : sourceNode.id,
    sourceHandleId: getSourceHandleId(sourceNode),
    targetNodeId: Array.isArray(targetNode) ? targetNode[0].id : targetNode.id,
    targetHandleId: getTargetHandleId(targetNode),
  }));
}
