import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { MapNodeContext } from "src/context/node-context/map-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { BaseNestedWorkflowNode } from "src/generators/nodes/bases/nested-workflow-base";
import { WorkflowProjectGenerator } from "src/project";
import { MapNode as MapNodeType, WorkflowRawData } from "src/types/vellum";

export class MapNode extends BaseNestedWorkflowNode<
  MapNodeType,
  MapNodeContext
> {
  getInnerWorkflowData(): WorkflowRawData {
    if (this.nodeData.data.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `MapNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    return this.nodeData.data.workflowRawData;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const items = this.getNodeInputByName("items");
    if (items) {
      const itemsField = python.field({
        name: "items",
        initializer: items,
      });
      statements.push(itemsField);
    }

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
    statements.push(subworkflowField);

    if (!isNil(this.nodeData.data.concurrency)) {
      const concurrencyField = python.field({
        name: "max_concurrency",
        initializer: python.TypeInstantiation.int(
          this.nodeData.data.concurrency
        ),
      });
      statements.push(concurrencyField);
    }

    return statements;
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

    return statements;
  }

  protected getNestedWorkflowProject(): WorkflowProjectGenerator {
    if (this.nodeData.data.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `MapNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    const mapNodeData = this.nodeData.data;
    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );

    return new WorkflowProjectGenerator({
      workflowVersionExecConfig: {
        workflowRawData: mapNodeData.workflowRawData,
        inputVariables: mapNodeData.inputVariables,
        stateVariables: [],
        outputVariables: mapNodeData.outputVariables,
      },
      moduleName: nestedWorkflowContext.moduleName,
      workflowContext: nestedWorkflowContext,
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
