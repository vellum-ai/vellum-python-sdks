import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { VELLUM_WORKFLOW_EDITOR_TYPES_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
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
  private readonly nodeDisplayData: AstNode;
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

  private generateNodeDisplayData(): python.ClassInstantiation {
    const args: python.MethodArgument[] = [];

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
      }),
      python.methodArgument({
        name: "width",
        value: this.sourceNodeDisplayData?.width
          ? python.TypeInstantiation.int(this.sourceNodeDisplayData.width)
          : python.TypeInstantiation.none(),
      }),
      python.methodArgument({
        name: "height",
        value: this.sourceNodeDisplayData?.height
          ? python.TypeInstantiation.int(this.sourceNodeDisplayData?.height)
          : python.TypeInstantiation.none(),
      })
    );

    const commentArg = this.generateCommentArg();
    if (commentArg) {
      args.push(commentArg);
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
          value: python.TypeInstantiation.str(value),
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

  public write(writer: Writer) {
    this.nodeDisplayData.write(writer);
  }
}
