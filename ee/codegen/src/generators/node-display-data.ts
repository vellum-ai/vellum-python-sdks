import { isNil } from "lodash";

import { VELLUM_WORKFLOW_EDITOR_TYPES_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { AstNode } from "src/generators/extensions/ast-node";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
import { NodeDisplayData as NodeDisplayDataType } from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export namespace NodeDisplayData {
  export interface Args {
    workflowContext: WorkflowContext;
    nodeDisplayData: NodeDisplayDataType | undefined;
  }
}

export class NodeDisplayData extends AstNode {
  private readonly sourceNodeDisplayData: NodeDisplayDataType | undefined;
  private readonly nodeDisplayData: AstNode | undefined;
  private readonly workflowContext: WorkflowContext;

  public constructor({
    nodeDisplayData,
    workflowContext,
  }: NodeDisplayData.Args) {
    super();
    this.sourceNodeDisplayData = nodeDisplayData;
    this.workflowContext = workflowContext;
    this.nodeDisplayData = this.generateNodeDisplayData();
  }

  public isEmpty(): boolean {
    return this.nodeDisplayData === undefined;
  }

  private generateNodeDisplayData(): ClassInstantiation | undefined {
    const args: MethodArgument[] = [];

    if (!isNil(this.sourceNodeDisplayData?.width)) {
      args.push(
        new MethodArgument({
          name: "width",
          value: new IntInstantiation(this.sourceNodeDisplayData.width),
        })
      );
    }

    if (!isNil(this.sourceNodeDisplayData?.height)) {
      args.push(
        new MethodArgument({
          name: "height",
          value: new IntInstantiation(this.sourceNodeDisplayData.height),
        })
      );
    }

    const commentArg = this.generateCommentArg();
    if (commentArg) {
      args.push(commentArg);
    }

    if (isNilOrEmpty(args)) {
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
          value: new BoolInstantiation(expanded),
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

  public write(writer: Writer) {
    if (this.nodeDisplayData) {
      this.nodeDisplayData.write(writer);
    }
  }
}
