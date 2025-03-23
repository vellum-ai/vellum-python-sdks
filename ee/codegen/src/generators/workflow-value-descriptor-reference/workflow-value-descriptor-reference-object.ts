import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import {
  IterableConfig,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";
import { isReference } from "src/utils/workflow-value-descriptor";

// This class is used to generate the WorkflowValueDescriptorReference as a class and not as the evaluation of the reference
export declare namespace WorkflowValueDescriptorReferenceObject {
  export interface Args {
    workflowContext: WorkflowContext;
    workflowValueDescriptor: WorkflowValueDescriptorType;
    iterableConfig?: IterableConfig;
  }
}

export class WorkflowValueDescriptorReferenceObject extends AstNode {
  private workflowContext: WorkflowContext;
  private iterableConfig?: IterableConfig;
  public astNode: AstNode | undefined;

  constructor(args: WorkflowValueDescriptorReferenceObject.Args) {
    super();

    this.workflowContext = args.workflowContext;
    this.iterableConfig = args.iterableConfig;

    this.astNode = this.getAstNode(args.workflowValueDescriptor);

    this.inheritReferences(this.astNode);
  }

  private getAstNode(
    workflowValueDescriptor: WorkflowValueDescriptorType | undefined
  ): AstNode | undefined {
    if (isNil(workflowValueDescriptor)) {
      return python.TypeInstantiation.none();
    }
    return this.buildExpression(workflowValueDescriptor);
  }

  private buildExpression(
    workflowValueDescriptor: WorkflowValueDescriptorType | undefined
  ): AstNode {
    if (!workflowValueDescriptor) {
      return python.TypeInstantiation.none();
    }

    // Base case
    if (isReference(workflowValueDescriptor)) {
      const workflowExpressionReference =
        this.buildWorkflowExpressionReferenceObject(workflowValueDescriptor);
      this.inheritReferences(workflowExpressionReference);
      return workflowExpressionReference;
    }

    switch (workflowValueDescriptor.type) {
      case "UNARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        return python.instantiateClass({
          classReference: python.reference({
            name: "UnaryWorkflowExpression",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "lhs",
              value: lhs,
            }),
            python.methodArgument({
              name: "operator",
              value: python.reference({
                name: "LogicalOperator",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .VELLUM_TYPES_MODULE_PATH,
                attribute: ["COALESCE"],
              }),
            }),
          ],
        });
      }
      case "BINARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        return python.instantiateClass({
          classReference: python.reference({
            name: "BinaryWorkflowExpression",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "lhs",
              value: lhs,
            }),
            python.methodArgument({
              name: "rhs",
              value: rhs,
            }),
            python.methodArgument({
              name: "operator",
              value: python.reference({
                name: "LogicalOperator",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .VELLUM_TYPES_MODULE_PATH,
                attribute: ["COALESCE"],
              }),
            }),
          ],
        });
      }
      case "TERNARY_EXPRESSION": {
        const base = this.buildExpression(workflowValueDescriptor.base);
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        return python.instantiateClass({
          classReference: python.reference({
            name: "TernaryWorkflowExpression",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "base",
              value: base,
            }),
            python.methodArgument({
              name: "lhs",
              value: lhs,
            }),
            python.methodArgument({
              name: "rhs",
              value: rhs,
            }),
            python.methodArgument({
              name: "operator",
              value: python.reference({
                name: "LogicalOperator",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .VELLUM_TYPES_MODULE_PATH,
                attribute: ["COALESCE"],
              }),
            }),
          ],
        });
      }
      default:
        assertUnreachable(workflowValueDescriptor);
    }
  }

  private buildWorkflowExpressionReferenceObject(
    workflowValueDescriptor: WorkflowValueDescriptorReferenceType
  ): AstNode {
    const referenceType = workflowValueDescriptor.type;

    switch (referenceType) {
      case "NODE_OUTPUT":
        return python.instantiateClass({
          classReference: python.reference({
            name: "NodeOutputWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "node_id",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.nodeId
              ),
            }),
            python.methodArgument({
              name: "node_output_id",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.nodeOutputId
              ),
            }),
          ],
        });
      case "WORKFLOW_INPUT":
        return python.instantiateClass({
          classReference: python.reference({
            name: "WorkflowInputWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "input_variable_id",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.inputVariableId
              ),
            }),
          ],
        });
      case "WORKFLOW_STATE":
        return python.instantiateClass({
          classReference: python.reference({
            name: "WorkflowStateVariableWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "state_variable_id",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.stateVariableId
              ),
            }),
          ],
        });
      case "CONSTANT_VALUE":
        return python.instantiateClass({
          classReference: python.reference({
            name: "WorkflowStateVariableWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "value",
              value: codegen.vellumValue({
                vellumValue: workflowValueDescriptor.value,
                iterableConfig: this.iterableConfig,
              }),
            }),
          ],
        });
      case "VELLUM_SECRET":
        return python.instantiateClass({
          classReference: python.reference({
            name: "VellumSecretWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "vellum_secret_name",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.vellumSecretName
              ),
            }),
          ],
        });
      case "EXECUTION_COUNTER":
        return python.instantiateClass({
          classReference: python.reference({
            name: "ExecutionCounterWorkflowReference",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "node_id",
              value: python.TypeInstantiation.str(
                workflowValueDescriptor.nodeId
              ),
            }),
          ],
        });
      default: {
        assertUnreachable(referenceType);
      }
    }
  }

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
