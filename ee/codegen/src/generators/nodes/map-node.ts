import { isNil } from "lodash";

import { MapNodeContext } from "src/context/node-context/map-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { Field } from "src/generators/extensions/field";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { TypeReference } from "src/generators/extensions/type-reference";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { BaseNestedWorkflowNode } from "src/generators/nodes/bases/nested-workflow-base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { WorkflowProjectGenerator } from "src/project";
import { MapNode as MapNodeType, WorkflowRawData } from "src/types/vellum";

export class MapNode extends BaseNestedWorkflowNode<
  MapNodeType,
  MapNodeContext
> {
  protected getNodeBaseGenericTypes(): AstNode[] | undefined {
    const [firstStateVariableContext] = Array.from(
      this.workflowContext.stateVariableContextsById.values()
    );

    // Only override if state is specified - otherwise fall back to base behavior
    // which generates class MapNode(BaseMapNode): without generics
    if (!firstStateVariableContext) {
      return undefined;
    }

    const stateType = this.getStateTypeOrBaseState();
    // MapNode requires two generic types: StateType and MapNodeItemType
    // We use Any as the item type since extracting the exact type from List[ItemType]
    // would require complex type inference
    const itemType = new TypeReference(
      new Reference({
        name: "Any",
        modulePath: ["typing"],
      })
    );
    return [stateType, itemType];
  }
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

    // Check for items attribute first (supports accessor patterns like PromptNode.Outputs.json["foo"])
    const itemsAttr = this.nodeData.attributes?.find(
      (attr) => attr.name === "items"
    );

    if (itemsAttr) {
      statements.push(
        new Field({
          name: "items",
          initializer: new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
            workflowValueDescriptor: itemsAttr.value,
          }),
        })
      );
    } else {
      // Fall back to legacy input-based items
      const items = this.getNodeInputByName("items");
      if (items) {
        const itemsField = new Field({
          name: "items",
          initializer: items,
        });
        statements.push(itemsField);
      }
    }

    const nestedWorkflowContext = this.getNestedWorkflowContextByName(
      BaseNestedWorkflowNode.subworkflowNestedProjectName
    );

    const nestedWorkflowReference = new Reference({
      name: nestedWorkflowContext.workflowClassName,
      modulePath: nestedWorkflowContext.modulePath,
    });

    const subworkflowField = new Field({
      name: "subworkflow",
      initializer: nestedWorkflowReference,
    });
    statements.push(subworkflowField);

    if (!isNil(this.nodeData.data.concurrency)) {
      const concurrencyField = new Field({
        name: "max_concurrency",
        initializer: new IntInstantiation(this.nodeData.data.concurrency),
      });
      statements.push(concurrencyField);
    }

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      new Field({
        name: "target_handle_id",
        initializer: new UuidInstantiation(this.nodeData.data.targetHandleId),
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
        stateVariables: mapNodeData.stateVariables ?? [],
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
