import { BaseNode } from "./base";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowDataNode } from "src/types/vellum";

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

  constructor(args: BaseNode.Args<T, V>) {
    super(args);

    this.nestedWorkflowContextsByName = this.generateNestedWorkflowContexts();
    this.nestedProjectsByName = this.generateNestedProjectsByName();
  }

  public getNestedProjects(): WorkflowProjectGenerator[] {
    return Array.from(this.nestedProjectsByName.values());
  }

  protected getNestedWorkflowContextByName(name: string): WorkflowContext {
    const nestedWorkflowContext = this.nestedWorkflowContextsByName.get(name);

    if (!nestedWorkflowContext) {
      throw new Error(
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
    const nestedWorkflowContext = new WorkflowContext({
      absolutePathToOutputDirectory:
        this.workflowContext.absolutePathToOutputDirectory,
      moduleName: this.workflowContext.moduleName,
      workflowLabel: nestedWorkflowLabel,
      inputVariableContextsById: this.workflowContext.inputVariableContextsById,
      nodeContextsByNodeId: this.workflowContext.nodeContextsByNodeId,
      parentNode: this,
      workflowsSdkModulePath:
        this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
    });

    return new Map([
      [
        BaseNestedWorkflowNode.subworkflowNestedProjectName,
        nestedWorkflowContext,
      ],
    ]);
  }
}