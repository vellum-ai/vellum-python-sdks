import { BaseNode } from "./base";

import { BaseNodeContext } from "src/context/node-context/base";
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
}
