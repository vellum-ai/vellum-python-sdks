import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNode } from "./base";

import { BaseNodeContext } from "src/context/node-context/base";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { WorkflowDataNode } from "src/types/vellum";

export abstract class BaseSingleFileNode<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BaseNode<T, V> {
  skipFormatting: boolean = false;

  public async persist(): Promise<void> {
    await Promise.all([
      this.getNodeFile().persist(this.skipFormatting),
      this.getNodeDisplayFile().persist(),
    ]);
  }

  public getNodeFile(): NodeImplementationFile<T, V> {
    return new NodeImplementationFile({ node: this });
  }

  public getNodeDisplayFile(): NodeDisplayFile<T, V> {
    return new NodeDisplayFile({ node: this });
  }
}

declare namespace NodeImplementationFile {
  interface Args<T extends WorkflowDataNode, V extends BaseNodeContext<T>> {
    node: BaseSingleFileNode<T, V>;
  }
}

class NodeImplementationFile<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BasePersistedFile {
  private readonly node: BaseNode<T, V>;

  constructor({ node }: NodeImplementationFile.Args<T, V>) {
    super({ workflowContext: node.workflowContext, isInitFile: false });

    this.node = node;
  }

  protected getModulePath(): string[] {
    return this.node.getNodeModulePath();
  }

  protected getFileStatements(): AstNode[] {
    return [this.node.generateNodeClass()];
  }
}

declare namespace NodeDisplayFile {
  interface Args<T extends WorkflowDataNode, V extends BaseNodeContext<T>> {
    node: BaseNode<T, V>;
  }
}

class NodeDisplayFile<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BasePersistedFile {
  private readonly node: BaseNode<T, V>;

  constructor({ node }: NodeDisplayFile.Args<T, V>) {
    super({ workflowContext: node.workflowContext, isInitFile: false });

    this.node = node;
  }

  protected getModulePath(): string[] {
    return this.node.getNodeDisplayModulePath();
  }

  protected getFileStatements(): AstNode[] {
    return this.node.generateNodeDisplayClasses();
  }
}
