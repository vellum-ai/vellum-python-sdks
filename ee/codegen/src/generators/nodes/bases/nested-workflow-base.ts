import { python } from "@fern-api/python-ast";

import { BaseNode } from "./base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
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

  protected getOutputDisplay(): Field {
    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );
    const outputVariableContexts = Array.from(
      nestedWorkflowContext.outputVariableContextsById.values()
    );

    return new Field({
      name: "output_display",
      initializer: new DictInstantiation(
        outputVariableContexts.map((outputContext) => {
          return {
            key: new Reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, outputContext.name],
            }),
            value: new ClassInstantiation({
              classReference: new Reference({
                name: "NodeOutputDisplay",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_TYPES_MODULE_PATH,
              }),
              arguments_: [
                new MethodArgument({
                  name: "id",
                  value: python.TypeInstantiation.uuid(
                    outputContext.getOutputVariableId()
                  ),
                }),
                new MethodArgument({
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
