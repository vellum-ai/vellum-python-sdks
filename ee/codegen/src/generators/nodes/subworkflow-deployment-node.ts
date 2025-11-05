import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { codegen } from "src/index";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";
import { toValidPythonIdentifier } from "src/utils/casing";

const INPUTS_PREFIX = "subworkflow_inputs";
const SUBWORKFLOW_INPUTS_CLASS_NAME = "SubworkflowInputs";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function getProp<T extends string>(obj: unknown, key: T): unknown {
  return isRecord(obj) ? obj[key] : undefined;
}

function hasInputsClassEnabled(wv: unknown, nodeId: string): boolean {
  if (!isRecord(wv)) return false;
  const moduleData = getProp(wv, "moduleData");
  if (!isRecord(moduleData)) return false;
  const workflowNodeModules = getProp(moduleData, "workflowNodeModules");
  if (!isRecord(workflowNodeModules)) return false;
  const nodeModule = getProp(workflowNodeModules, nodeId);
  if (!isRecord(nodeModule)) return false;
  const hasInputsClass = getProp(nodeModule, "hasInputsClass");
  return hasInputsClass === true;
}

export class SubworkflowDeploymentNode extends BaseNode<
  SubworkflowNodeType,
  SubworkflowDeploymentNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  public async persist(): Promise<void> {
    const inputsFile = this.getNodeInputsFile();
    const persistPromises = [
      this.getNodeFile().persist(),
      this.getNodeDisplayFile().persist(),
    ];

    if (inputsFile) {
      persistPromises.push(inputsFile.persist());
    }

    await Promise.all(persistPromises);
  }

  public getNodeInputsFile(): NodeInputsFile | null {
    const workflowVersion =
      this.nodeContext.workflowDeploymentRelease?.workflowVersion;
    if (!workflowVersion) {
      return null;
    }

    if (!hasInputsClassEnabled(workflowVersion, this.nodeData.id)) {
      return null;
    }

    const inputVariables = workflowVersion.inputVariables;
    if (inputVariables.length === 0) {
      return null;
    }

    if (this.nodeInputsByKey.size === 0) {
      return null;
    }

    return new NodeInputsFile({ node: this });
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
        python.field({
          name: "deployment",
          initializer: python.TypeInstantiation.str(
            this.nodeContext.workflowDeploymentRelease.deployment.name
          ),
        })
      );
    }

    statements.push(
      python.field({
        name: "release_tag",
        initializer: python.TypeInstantiation.str(
          this.nodeData.data.releaseTag
        ),
      })
    );

    const hasInputsFile = this.getNodeInputsFile() !== null;
    statements.push(this.generateSubworkflowInputsInitializer(hasInputsFile));

    const outputsClass = this.generateOutputsClass();
    if (outputsClass) {
      statements.push(outputsClass);
    }

    return statements;
  }

  private generateOutputsClass(): python.Class | null {
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
    const outputsClass = python.class_({
      name: OUTPUTS_CLASS_NAME,
      extends_: [
        python.reference({
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
                name: outputName,
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

  public generateSubworkflowInputsClass(): python.Class | null {
    if (!this.nodeContext.workflowDeploymentRelease) {
      return null;
    }

    const workflowVersion =
      this.nodeContext.workflowDeploymentRelease.workflowVersion;
    if (!hasInputsClassEnabled(workflowVersion, this.nodeData.id)) {
      return null;
    }

    const inputVariables =
      this.nodeContext.workflowDeploymentRelease.workflowVersion.inputVariables;

    if (inputVariables.length === 0) {
      return null;
    }

    if (this.nodeInputsByKey.size === 0) {
      return null;
    }

    const baseInputsClassReference = python.reference({
      name: "BaseInputs",
      modulePath: this.workflowContext.sdkModulePathNames.INPUTS_MODULE_PATH,
    });

    const inputsClass = python.class_({
      name: SUBWORKFLOW_INPUTS_CLASS_NAME,
      extends_: [baseInputsClassReference],
    });

    const sanitizedNames = new Set<string>();
    let hasCollision = false;

    inputVariables.forEach((inputVariable) => {
      const sanitizedName = toValidPythonIdentifier(inputVariable.key, "input");

      if (sanitizedNames.has(sanitizedName)) {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            `Failed to generate ${this.nodeData.data.label}.${SUBWORKFLOW_INPUTS_CLASS_NAME}: duplicate input name "${sanitizedName}" after sanitization`,
            "WARNING"
          )
        );
        hasCollision = true;
        return;
      }

      sanitizedNames.add(sanitizedName);

      const vellumVariableField = codegen.vellumVariable({
        variable: {
          id: inputVariable.id,
          name: sanitizedName,
          type: inputVariable.type,
          required: inputVariable.required,
          default: inputVariable.default,
        },
        defaultRequired: false,
      });

      inputsClass.add(vellumVariableField);
    });

    if (hasCollision) {
      return null;
    }

    return inputsClass;
  }

  private generateSubworkflowInputsInitializer(
    hasInputsFile: boolean
  ): python.Field {
    if (
      hasInputsFile &&
      this.nodeContext.workflowDeploymentRelease &&
      this.nodeInputsByKey.size > 0
    ) {
      const inputVariables =
        this.nodeContext.workflowDeploymentRelease.workflowVersion
          .inputVariables;

      const arguments_: python.MethodArgument[] = [];

      inputVariables.forEach((inputVariable) => {
        const sanitizedName = toValidPythonIdentifier(
          inputVariable.key,
          "input"
        );

        const nodeInput = this.nodeInputsByKey.get(inputVariable.key);
        if (nodeInput) {
          arguments_.push(
            python.methodArgument({
              name: sanitizedName,
              value: nodeInput,
            })
          );
        }
      });

      return python.field({
        name: INPUTS_PREFIX,
        initializer: python.instantiateClass({
          classReference: python.reference({
            name: SUBWORKFLOW_INPUTS_CLASS_NAME,
            modulePath: [...this.nodeContext.nodeModulePath, "inputs"],
          }),
          arguments_,
        }),
      });
    }

    return python.field({
      name: INPUTS_PREFIX,
      initializer: python.TypeInstantiation.dict(
        Array.from(this.nodeInputsByKey.entries()).map(([key, value]) => ({
          key: python.TypeInstantiation.str(key),
          value: value,
        })),
        {
          endWithComma: true,
        }
      ),
    });
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

  protected getOutputDisplay(): python.Field | undefined {
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

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        outputVariables.map((output) => {
          const outputName = this.nodeContext.getNodeOutputNameById(output.id);
          if (!outputName) {
            throw new NodeAttributeGenerationError(
              `Could not find output name for ${this.nodeContext.nodeClassName}.Outputs.${output.key} given output id ${output.id}`
            );
          }
          return {
            key: python.reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, outputName],
            }),
            value: python.instantiateClass({
              classReference: python.reference({
                name: "NodeOutputDisplay",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_TYPES_MODULE_PATH,
              }),
              arguments_: [
                python.methodArgument({
                  name: "id",
                  value: python.TypeInstantiation.uuid(output.id),
                }),
                python.methodArgument({
                  name: "name",
                  value: python.TypeInstantiation.str(output.key),
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

declare namespace NodeInputsFile {
  interface Args {
    node: SubworkflowDeploymentNode;
  }
}

class NodeInputsFile extends BasePersistedFile {
  private readonly node: SubworkflowDeploymentNode;

  constructor({ node }: NodeInputsFile.Args) {
    super({ workflowContext: node.workflowContext, isInitFile: false });
    this.node = node;
  }

  protected getModulePath(): string[] {
    return [...this.node.getNodeModulePath(), "inputs"];
  }

  protected getFileStatements(): AstNode[] {
    const inputsClass = this.node.generateSubworkflowInputsClass();
    if (!inputsClass) {
      return [];
    }
    return [inputsClass];
  }

  public async persist(): Promise<void> {
    await super.persist();
  }
}
