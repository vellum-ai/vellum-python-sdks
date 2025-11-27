import { python } from "@fern-api/python-ast";

import { BaseNode } from "./base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowDataNode, WorkflowRawData } from "src/types/vellum";

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
    const nestedWorkflowClassName =
      this.workflowContext.getUniqueClassName(nestedWorkflowLabel);
    this.workflowContext.addUsedClassName(nestedWorkflowClassName);

    const innerWorkflowData = this.getInnerWorkflowData();

    const nestedWorkflowContext =
      this.workflowContext.createNestedWorkflowContext({
        parentNode: this,
        workflowClassName: nestedWorkflowClassName,
        workflowRawData: innerWorkflowData,
        classNames: this.workflowContext.classNames,
      });

    return new Map([
      [
        BaseNestedWorkflowNode.subworkflowNestedProjectName,
        nestedWorkflowContext,
      ],
    ]);
  }

  protected getOutputDisplay(): python.Field {
    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );
    const outputVariableContexts = Array.from(
      nestedWorkflowContext.outputVariableContextsById.values()
    );

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        outputVariableContexts.map((outputContext) => {
          return {
            key: python.reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, outputContext.name],
            }),
            value: python.instantiateClass({
              classReference: python.reference({
                name: "NodeOutputDisplay",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_TYPES_MODULE_PATH,
              }),
              arguments_: [
                python.methodArgument({
                  name: "id",
                  value: python.TypeInstantiation.uuid(
                    outputContext.getOutputVariableId()
                  ),
                }),
                python.methodArgument({
                  name: "name",
                  value: new StrInstantiation(outputContext.getRawName()),
                }),
              ],
            }),
          };
        })
      ),
    });
  }
}
