import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { LambdaInstantiation } from "src/generators/extensions/lambda-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { ExecutionCounterWorkflowReference as ExecutionCounterWorkflowReferenceType } from "src/types/vellum";

export class ExecutionCounterWorkflowReference extends BaseNodeInputWorkflowReference<ExecutionCounterWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const executionCounterNodeId =
      this.nodeInputWorkflowReferencePointer.nodeId;

    const nodeContext = this.workflowContext.findNodeContext(
      executionCounterNodeId
    );

    if (!nodeContext) {
      return undefined;
    }

    const reference = new Reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });

    const hasReferenceToSelf = this.hasReferenceToSelf(executionCounterNodeId);
    if (hasReferenceToSelf) {
      return new ClassInstantiation({
        classReference: new Reference({
          name: "LazyReference",
          modulePath: [
            ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          new MethodArgument({
            value: new LambdaInstantiation({
              body: reference,
            }),
          }),
        ],
      });
    }

    return reference;
  }

  private hasReferenceToSelf(referencedNodeId: string): boolean {
    if (!this.nodeContext) {
      return false;
    }

    const currentNodeId = this.nodeContext.nodeData?.id;

    return currentNodeId === referencedNodeId;
  }
}
