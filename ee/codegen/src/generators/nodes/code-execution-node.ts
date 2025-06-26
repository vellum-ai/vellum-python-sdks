import { mkdir, writeFile } from "fs/promises";
import * as path from "path";

import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { InitFile } from "src/generators";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { CodeExecutionNode as CodeExecutionNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

const CODE_INPUT_KEY = "code";
const RUNTIME_INPUT_KEY = "runtime";
const INPUTS_PREFIX = "code_inputs";

export class CodeExecutionNode extends BaseNode<
  CodeExecutionNodeType,
  CodeExecutionContext
> {
  public declare readonly nodeContext: CodeExecutionContext;
  private readonly scriptFileContents: string;

  constructor({
    workflowContext,
    nodeContext,
  }: BaseNode.Args<CodeExecutionNodeType, CodeExecutionContext>) {
    super({ workflowContext, nodeContext });
    this.scriptFileContents = this.generateScriptFileContents();
  }

  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    if (nodeInputKey === CODE_INPUT_KEY) {
      return nodeInputKey;
    }
    if (nodeInputKey === RUNTIME_INPUT_KEY) {
      return nodeInputKey;
    }

    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  // Override
  public async persist(): Promise<void> {
    const nodeInitFile = new InitFile({
      workflowContext: this.workflowContext,
      modulePath: this.nodeContext.nodeModulePath,
      statements: [this.generateNodeClass()],
    });

    await Promise.all([
      nodeInitFile.persist(),
      this.persistScriptFile(),
      this.getNodeDisplayFile().persist(),
    ]);
  }

  protected getNodeBaseGenericTypes(): AstNode[] {
    const stateType = this.getStateTypeOrBaseState();
    const primitiveOutputType = getVellumVariablePrimitiveType(
      this.nodeData.data.outputType
    );
    return [stateType, primitiveOutputType];
  }

  getNodeClassBodyStatements(): AstNode[] {
    const nodeData = this.nodeData.data;
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "filepath",
        initializer: python.TypeInstantiation.str(this.nodeContext.filepath),
      })
    );

    const systemInputs = [nodeData.codeInputId, nodeData.runtimeInputId];
    const codeInputs = Array.from(this.nodeInputsByKey.values()).filter(
      (nodeInput) => !systemInputs.includes(nodeInput.nodeInputData.id)
    );

    statements.push(
      python.field({
        name: INPUTS_PREFIX,
        initializer: python.TypeInstantiation.dict(
          codeInputs.map((codeInput) => ({
            key: python.TypeInstantiation.str(codeInput.nodeInputData.key),
            value: codeInput,
          })),
          {
            endWithComma: true,
          }
        ),
      })
    );

    const runtime = this.nodeContext.getRuntime();

    if (runtime) {
      statements.push(
        python.field({
          name: RUNTIME_INPUT_KEY,
          initializer: python.TypeInstantiation.str(runtime),
        })
      );
    }

    statements.push(
      python.field({
        name: "packages",
        initializer: nodeData.packages
          ? python.TypeInstantiation.list(
              nodeData.packages.map((package_) =>
                python.instantiateClass({
                  classReference: python.reference({
                    name: "CodeExecutionPackage",
                    modulePath: ["vellum", "types"],
                  }),
                  arguments_: [
                    python.methodArgument({
                      name: "name",
                      value: python.TypeInstantiation.str(package_.name),
                    }),
                    python.methodArgument({
                      name: "version",
                      value: python.TypeInstantiation.str(package_.version),
                    }),
                  ],
                })
              ),
              {
                endWithComma: true,
              }
            )
          : python.TypeInstantiation.none(),
      })
    );

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const nodeData = this.nodeData.data;
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
        name: "output_id",
        initializer: python.TypeInstantiation.uuid(nodeData.outputId),
      })
    );

    if (nodeData.logOutputId) {
      statements.push(
        python.field({
          name: "log_output_id",
          initializer: nodeData.logOutputId
            ? python.TypeInstantiation.uuid(nodeData.logOutputId)
            : python.TypeInstantiation.none(),
        })
      );
    }

    return statements;
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  private generateScriptFileContents(): string {
    const codeInputId = this.nodeData.data.codeInputId;
    const codeInput = this.nodeData.inputs.find(
      (nodeInput) => nodeInput.id === codeInputId
    );

    const codeInputRule = codeInput?.value.rules[0];
    if (
      !codeInputRule ||
      codeInputRule.type !== "CONSTANT_VALUE" ||
      codeInputRule.data.type !== "STRING"
    ) {
      throw new NodeAttributeGenerationError(
        "Expected to find code input with constant string value"
      );
    }

    const scriptFileContents = codeInputRule.data.value ?? "";
    return scriptFileContents;
  }

  private async persistScriptFile(): Promise<void> {
    const runtimeRuleInput = this.getNodeInputByName("runtime");
    const runtimeRule = runtimeRuleInput?.nodeInputData?.value?.rules[0];
    let runtime;
    if (
      !runtimeRule ||
      runtimeRule.type !== "CONSTANT_VALUE" ||
      runtimeRule.data.type !== "STRING"
    ) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Expected to find runtime input with constant string value"
        )
      );
      runtime = "";
    } else {
      runtime = runtimeRule?.data?.value ?? "";
    }
    const filepath =
      this.nodeData.data.filepath ?? runtime?.includes("TYPESCRIPT")
        ? "./script.ts"
        : "./script.py";

    const absolutPathToNodeDirectory = `${
      this.workflowContext.absolutePathToOutputDirectory
    }/${this.nodeContext.nodeModulePath.join("/")}`;

    let absolutePathToScriptFile: string;
    if (path.isAbsolute(filepath)) {
      absolutePathToScriptFile = filepath;
    } else {
      // Resolve it relative to the basePath
      absolutePathToScriptFile = path.resolve(
        absolutPathToNodeDirectory,
        filepath
      );
    }
    await mkdir(path.dirname(absolutePathToScriptFile), { recursive: true });
    await writeFile(absolutePathToScriptFile, this.scriptFileContents);
    return;
  }

  protected getOutputDisplay(): python.Field {
    const outputDisplayEntries = [
      {
        key: python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "result"],
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
              value: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
            }),
            python.methodArgument({
              name: "name",
              value: python.TypeInstantiation.str("result"),
            }),
          ],
        }),
      },
    ];

    if (this.nodeData.data.logOutputId) {
      outputDisplayEntries.push({
        key: python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "log"],
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
              value: python.TypeInstantiation.uuid(
                this.nodeData.data.logOutputId
              ),
            }),
            python.methodArgument({
              name: "name",
              value: python.TypeInstantiation.str("log"),
            }),
          ],
        }),
      });
    }

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(outputDisplayEntries),
    });
  }
}
