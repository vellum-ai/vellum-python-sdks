import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { InlineSubworkflowNodeContext } from "src/context/node-context/inline-subworkflow-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { BaseNestedWorkflowNode } from "src/generators/nodes/bases/nested-workflow-base";
import { WorkflowProjectGenerator } from "src/project";
import {
  SubworkflowNode as SubworkflowNodeType,
  WorkflowRawData,
} from "src/types/vellum";

export class InlineSubworkflowNode extends BaseNestedWorkflowNode<
  SubworkflowNodeType,
  InlineSubworkflowNodeContext
> {
  getInnerWorkflowData(): WorkflowRawData {
    if (this.nodeData.data.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `InlineSubworkflowNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    return this.nodeData.data.workflowRawData;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );

    const nestedWorkflowReference = python.reference({
      name: nestedWorkflowContext.workflowClassName,
      modulePath: nestedWorkflowContext.modulePath,
    });

    const subworkflowField = python.field({
      name: "subworkflow",
      initializer: nestedWorkflowReference,
    });

    return [subworkflowField];
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    statements.push(
      python.field({
        name: "workflow_input_ids_by_name",
        initializer: python.TypeInstantiation.dict([]),
      })
    );

    return statements;
  }

  protected getNestedWorkflowProject(): WorkflowProjectGenerator {
    if (this.nodeData.data.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    const inlineSubworkflowNodeData = this.nodeData.data;
    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );

    return new WorkflowProjectGenerator({
      workflowVersionExecConfig: {
        workflowRawData: inlineSubworkflowNodeData.workflowRawData,
        inputVariables: inlineSubworkflowNodeData.inputVariables,
        stateVariables: [],
        outputVariables: inlineSubworkflowNodeData.outputVariables,
      },
      moduleName: nestedWorkflowContext.moduleName,
      workflowContext: nestedWorkflowContext,
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
