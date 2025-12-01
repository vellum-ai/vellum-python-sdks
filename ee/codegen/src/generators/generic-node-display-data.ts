import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { VELLUM_WORKFLOW_EDITOR_TYPES_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
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

  private generateNodeDisplayData(): ClassInstantiation | undefined {
    const args: MethodArgument[] = [];

    // Only add position if at least one coordinate is provided
    if (
      !isNil(this.sourceNodeDisplayData?.position?.x) ||
      !isNil(this.sourceNodeDisplayData?.position?.y)
    ) {
      args.push(
        new MethodArgument({
          name: "position",
          value: new ClassInstantiation({
            classReference: new Reference({
              name: "NodeDisplayPosition",
              modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
            }),
            arguments_: [
              new MethodArgument({
                name: "x",
                value: python.TypeInstantiation.float(
                  this.sourceNodeDisplayData?.position?.x ?? 0
                ),
              }),
              new MethodArgument({
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
        new MethodArgument({
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
        new MethodArgument({
          name: "icon",
          value: new StrInstantiation(this.sourceNodeDisplayData.icon),
        })
      );
    }

    if (!isNil(this.sourceNodeDisplayData?.color)) {
      args.push(
        new MethodArgument({
          name: "color",
          value: new StrInstantiation(this.sourceNodeDisplayData.color),
        })
      );
    }

    // Return undefined if no display data fields are provided
    if (args.length === 0) {
      return undefined;
    }

    const clazz = new ClassInstantiation({
      classReference: new Reference({
        name: "NodeDisplayData",
        modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
      }),
      arguments_: args,
    });
    this.inheritReferences(clazz);
    return clazz;
  }

  private generateCommentArg(): MethodArgument | undefined {
    if (!this.sourceNodeDisplayData?.comment) {
      return undefined;
    }

    const commentArgs: MethodArgument[] = [];
    const { expanded, value } = this.sourceNodeDisplayData.comment;

    if (expanded) {
      commentArgs.push(
        new MethodArgument({
          name: "expanded",
          value: python.TypeInstantiation.bool(expanded),
        })
      );
    }

    if (value) {
      commentArgs.push(
        new MethodArgument({
          name: "value",
          value: new StrInstantiation(value),
        })
      );
    }

    if (isNilOrEmpty(commentArgs)) {
      return undefined;
    }

    return new MethodArgument({
      name: "comment",
      value: new ClassInstantiation({
        classReference: new Reference({
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
