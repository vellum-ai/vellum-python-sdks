import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

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

    const reference = python.reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });

    const hasReferenceToSelf = this.hasReferenceToSelf(executionCounterNodeId);
    if (hasReferenceToSelf) {
      return python.instantiateClass({
        classReference: python.reference({
          name: "LazyReference",
          modulePath: [
            ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          python.methodArgument({
            value: python.lambda({
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
