import { OUTPUTS_CLASS_NAME } from "src/constants";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { BaseNode } from "src/generators/nodes/bases/base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { codegen } from "src/index";
import {
  SubworkflowNode as SubworkflowNodeType,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";
import { isExpression, isReference } from "src/utils/workflow-value-descriptor";

const INPUTS_PREFIX = "subworkflow_inputs";

function isWorkflowValueDescriptor(
  value: unknown
): value is WorkflowValueDescriptorType {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const obj = value as Record<string, unknown>;
  if (typeof obj.type !== "string") {
    return false;
  }
  return (
    isExpression(obj as unknown as WorkflowValueDescriptorType) ||
    isReference(obj as unknown as WorkflowValueDescriptorType)
  );
}

export class SubworkflowDeploymentNode extends BaseNode<
  SubworkflowNodeType,
  SubworkflowDeploymentNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  private getSubworkflowInputEntries(): Array<{
    key: AstNode;
    value: AstNode;
  }> {
    const entries: Array<{ key: AstNode; value: AstNode }> = [];

    const nodeInputs = this.nodeData.inputs ?? [];
    for (const nodeInput of nodeInputs) {
      // First, check if this is an expression-valued JSON input
      const rules = nodeInput.value?.rules ?? [];
      let foundExpression = false;
      for (const rule of rules) {
        if (rule.type === "CONSTANT_VALUE" && rule.data.type === "JSON") {
          const jsonValue = rule.data.value;
          if (isWorkflowValueDescriptor(jsonValue)) {
            entries.push({
              key: new StrInstantiation(nodeInput.key),
              value: new WorkflowValueDescriptor({
                nodeContext: this.nodeContext,
                workflowContext: this.workflowContext,
                workflowValueDescriptor: jsonValue,
                iterableConfig: { endWithComma: true },
              }),
            });
            foundExpression = true;
            break;
          }
        }
      }

      if (foundExpression) {
        continue;
      }

      // Otherwise, use the existing node input if available
      const existingNodeInput = this.nodeInputsByKey.get(nodeInput.key);
      if (existingNodeInput) {
        entries.push({
          key: new StrInstantiation(nodeInput.key),
          value: existingNodeInput,
        });
      }
    }

    return entries;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowDeploymentNode only supports DEPLOYMENT variant. Received ${this.nodeData.data.variant}`
      );
    }

    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Failed to generate attribute: ${this.nodeData.data.label}.deployment`,
          "WARNING"
        )
      );
    } else {
      statements.push(
        new Field({
          name: "deployment",
          initializer: new StrInstantiation(
            this.nodeContext.workflowDeploymentRelease.deployment.name
          ),
        })
      );
    }

    statements.push(
      new Field({
        name: "release_tag",
        initializer: new StrInstantiation(this.nodeData.data.releaseTag),
      })
    );

    statements.push(
      new Field({
        name: INPUTS_PREFIX,
        initializer: new DictInstantiation(this.getSubworkflowInputEntries(), {
          endWithComma: true,
        }),
      })
    );

    const outputsClass = this.generateOutputsClass();
    if (outputsClass) {
      statements.push(outputsClass);
    }

    return statements;
  }

  private generateOutputsClass(): Class | null {
    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Failed to generate ${this.nodeData.data.label}.Outputs class`,
          "WARNING"
        )
      );
      return null;
    }

    const nodeBaseClassRef = this.getNodeBaseClass();
    const outputsClass = new Class({
      name: OUTPUTS_CLASS_NAME,
      extends_: [
        new Reference({
          name: nodeBaseClassRef.name,
          modulePath: nodeBaseClassRef.modulePath,
          alias: nodeBaseClassRef.alias,
          attribute: [OUTPUTS_CLASS_NAME],
        }),
      ],
    });

    this.nodeContext.workflowDeploymentRelease.workflowVersion.outputVariables.forEach(
      (output) => {
        const outputName = this.nodeContext.getNodeOutputNameById(output.id);
        if (outputName) {
          outputsClass.add(
            codegen.vellumVariable({
              variable: {
                key: outputName,
                type: output.type,
                id: output.id,
                required: output.required,
              },
              defaultRequired: true,
            })
          );
        }
      }
    );

    return outputsClass;
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

  protected getOutputDisplay(): Field | undefined {
    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeDefinitionGenerationError(
          `Failed to generate \`output_display\` for ${this.nodeData.data.label}`,
          "WARNING"
        )
      );
    }

    const outputVariables =
      this.nodeContext.workflowDeploymentRelease?.workflowVersion
        .outputVariables ?? [];

    return new Field({
      name: "output_display",
      initializer: new DictInstantiation(
        outputVariables.map((output) => {
          const outputName = this.nodeContext.getNodeOutputNameById(output.id);
          if (!outputName) {
            throw new NodeAttributeGenerationError(
              `Could not find output name for ${this.nodeContext.nodeClassName}.Outputs.${output.key} given output id ${output.id}`
            );
          }
          return {
            key: new Reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, outputName],
            }),
            value: new ClassInstantiation({
              classReference: new Reference({
                name: "NodeOutputDisplay",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_TYPES_MODULE_PATH,
              }),
              arguments_: [
                new MethodArgument({
                  name: "id",
                  value: new UuidInstantiation(output.id),
                }),
                new MethodArgument({
                  name: "name",
                  value: new StrInstantiation(output.key),
                }),
              ],
            }),
          };
        })
      ),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
