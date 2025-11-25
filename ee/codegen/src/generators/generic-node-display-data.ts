import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { VELLUM_WORKFLOW_EDITOR_TYPES_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
import { GenericNodeDisplayData as GenericNodeDisplayDataType } from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export namespace GenericNodeDisplayData {
  export interface Args {
    workflowContext: WorkflowContext;
    nodeDisplayData: GenericNodeDisplayDataType | undefined;
  }
}

export class GenericNodeDisplayData extends AstNode {
  private readonly sourceNodeDisplayData:
    | GenericNodeDisplayDataType
    | undefined;
  private readonly nodeDisplayData: AstNode | undefined;
  private readonly workflowContext: WorkflowContext;

  public constructor({
    nodeDisplayData,
    workflowContext,
  }: GenericNodeDisplayData.Args) {
    super();
    this.sourceNodeDisplayData = nodeDisplayData;
    this.workflowContext = workflowContext;
    this.nodeDisplayData = this.generateNodeDisplayData();
  }

  private generateNodeDisplayData(): python.ClassInstantiation | undefined {
    const args: python.MethodArgument[] = [];

    // Only add position if at least one coordinate is provided
    if (
      !isNil(this.sourceNodeDisplayData?.position?.x) ||
      !isNil(this.sourceNodeDisplayData?.position?.y)
    ) {
      args.push(
        python.methodArgument({
          name: "position",
          value: python.instantiateClass({
            classReference: python.reference({
              name: "NodeDisplayPosition",
              modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "x",
                value: python.TypeInstantiation.float(
                  this.sourceNodeDisplayData?.position?.x ?? 0
                ),
              }),
              python.methodArgument({
                name: "y",
                value: python.TypeInstantiation.float(
                  this.sourceNodeDisplayData?.position?.y ?? 0
                ),
              }),
            ],
          }),
        })
      );
    }

    if (!isNil(this.sourceNodeDisplayData?.z_index)) {
      args.push(
        python.methodArgument({
          name: "z_index",
          value: python.TypeInstantiation.int(
            this.sourceNodeDisplayData.z_index
          ),
        })
      );
    }

    const commentArg = this.generateCommentArg();
    if (commentArg) {
      args.push(commentArg);
    }

    if (!isNil(this.sourceNodeDisplayData?.icon)) {
      args.push(
        python.methodArgument({
          name: "icon",
          value: new StrInstantiation(this.sourceNodeDisplayData.icon),
        })
      );
    }

    if (!isNil(this.sourceNodeDisplayData?.color)) {
      args.push(
        python.methodArgument({
          name: "color",
          value: new StrInstantiation(this.sourceNodeDisplayData.color),
        })
      );
    }

    // Return undefined if no display data fields are provided
    if (args.length === 0) {
      return undefined;
    }

    const clazz = python.instantiateClass({
      classReference: python.reference({
        name: "NodeDisplayData",
        modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
      }),
      arguments_: args,
    });
    this.inheritReferences(clazz);
    return clazz;
  }

  private generateCommentArg(): python.MethodArgument | undefined {
    if (!this.sourceNodeDisplayData?.comment) {
      return undefined;
    }

    const commentArgs: python.MethodArgument[] = [];
    const { expanded, value } = this.sourceNodeDisplayData.comment;

    if (expanded) {
      commentArgs.push(
        python.methodArgument({
          name: "expanded",
          value: python.TypeInstantiation.bool(expanded),
        })
      );
    }

    if (value) {
      commentArgs.push(
        python.methodArgument({
          name: "value",
          value: new StrInstantiation(value),
        })
      );
    }

    if (isNilOrEmpty(commentArgs)) {
      return undefined;
    }

    return python.methodArgument({
      name: "comment",
      value: python.instantiateClass({
        classReference: python.reference({
          name: "NodeDisplayComment",
          modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
        }),
        arguments_: commentArgs,
      }),
    });
  }

  public hasContent(): boolean {
    return this.nodeDisplayData !== undefined;
  }

  public write(writer: Writer) {
    if (this.nodeDisplayData) {
      this.nodeDisplayData.write(writer);
    }
  }
}
