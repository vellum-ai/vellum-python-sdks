import {
  AdornmentNode,
  NodeAttribute,
  NodeOutput,
  NodePort,
  WorkflowDataNode as WorkflowDataNodeType,
} from "src/types/vellum";

export class NodeDataFactoryBuilder<T extends WorkflowDataNodeType> {
  public nodeData: T;

  constructor(nodeData: T) {
    this.nodeData = nodeData;
  }

  withPorts(ports: NodePort[]): NodeDataFactoryBuilder<T> {
    this.nodeData = {
      ...this.nodeData,
      ports: ports,
    };
    return this;
  }

  withAttributes(attributes: NodeAttribute[]): NodeDataFactoryBuilder<T> {
    this.nodeData = {
      ...this.nodeData,
      attributes,
    };
    return this;
  }

  withAdornments(adornments: AdornmentNode[]): NodeDataFactoryBuilder<T> {
    this.nodeData = {
      ...this.nodeData,
      adornments,
    };
    return this;
  }

  withOutputs(outputs: NodeOutput[]): NodeDataFactoryBuilder<T> {
    this.nodeData = {
      ...this.nodeData,
      outputs,
    };
    return this;
  }

  build(): T {
    return this.nodeData;
  }
}
