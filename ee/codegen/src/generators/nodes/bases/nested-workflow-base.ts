import { BaseNode } from "./base";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowDataNode, WorkflowRawData } from "src/types/vellum";
import { createPythonClassName } from "src/utils/casing";

export abstract class BaseNestedWorkflowNode<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BaseNode<T, V> {
  protected static readonly subworkflowNestedProjectName = "subworkflow";
  protected readonly nestedWorkflowContextsByName: Map<string, WorkflowContext>;
  protected readonly nestedProjectsByName: Map<
    string,
    WorkflowProjectGenerator
  >;

  protected abstract getNestedWorkflowProject(): WorkflowProjectGenerator;

  protected abstract getInnerWorkflowData(): WorkflowRawData;

  constructor(args: BaseNode.Args<T, V>) {
    super(args);

    this.nestedWorkflowContextsByName = this.generateNestedWorkflowContexts();
    this.nestedProjectsByName = this.generateNestedProjectsByName();
  }

  public async persist(): Promise<void> {
    const nestedProjects = this.getNestedProjects();
    await Promise.all(nestedProjects.map((project) => project.generateCode()));
  }

  private getNestedProjects(): WorkflowProjectGenerator[] {
    return Array.from(this.nestedProjectsByName.values());
  }

  protected getNestedWorkflowContextByName(name: string): WorkflowContext {
    const nestedWorkflowContext = this.nestedWorkflowContextsByName.get(name);

    if (!nestedWorkflowContext) {
      throw new NodeAttributeGenerationError(
        `Nested workflow context not found for attribute name: ${name}`
      );
    }

    return nestedWorkflowContext;
  }

  protected generateNestedProjectsByName(): Map<
    string,
    WorkflowProjectGenerator
  > {
    return new Map([
      [
        BaseNestedWorkflowNode.subworkflowNestedProjectName,
        this.getNestedWorkflowProject(),
      ],
    ]);
  }

  protected generateNestedWorkflowContexts(): Map<string, WorkflowContext> {
    const nestedWorkflowLabel = `${this.nodeContext.getNodeLabel()} Workflow`;
    const nestedWorkflowClassName = createPythonClassName(nestedWorkflowLabel);

    const innerWorkflowData = this.getInnerWorkflowData();

    const nestedWorkflowContext =
      this.workflowContext.createNestedWorkflowContext({
        parentNode: this,
        workflowClassName: nestedWorkflowClassName,
        workflowRawEdges: innerWorkflowData.edges,
      });

    return new Map([
      [
        BaseNestedWorkflowNode.subworkflowNestedProjectName,
        nestedWorkflowContext,
      ],
    ]);
  }
}
