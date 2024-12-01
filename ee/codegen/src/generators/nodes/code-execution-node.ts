import { mkdir, writeFile } from "fs/promises";
import * as path from "path";

import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { InitFile } from "src/generators";
import { BaseState } from "src/generators/base-state";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { CodeExecutionNode as CodeExecutionNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

export class CodeExecutionNode extends BaseSingleFileNode<
  CodeExecutionNodeType,
  CodeExecutionContext
> {
  public declare readonly nodeContext: CodeExecutionContext;

  baseNodeClassName = "CodeExecutionNode";
  baseNodeDisplayClassName = "BaseCodeExecutionNodeDisplay";

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
    const baseStateClassReference = new BaseState({
      workflowContext: this.workflowContext,
    });

    const primitiveOutputType = getVellumVariablePrimitiveType(
      this.nodeData.data.outputType
    );

    return [baseStateClassReference, primitiveOutputType];
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
        name: "code_inputs",
        initializer: python.TypeInstantiation.dict(
          codeInputs.map((codeInput) => ({
            key: python.TypeInstantiation.str(codeInput.nodeInputData.key),
            value: codeInput,
          }))
        ),
      })
    );

    statements.push(
      python.field({
        name: "output_type",
        initializer: python.TypeInstantiation.str(nodeData.outputType),
      })
    );

    statements.push(
      python.field({
        name: "runtime",
        initializer: this.getNodeInputByName("runtime"),
      })
    );

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
              )
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
        name: "code_input_id",
        initializer: python.TypeInstantiation.uuid(nodeData.codeInputId),
      })
    );

    statements.push(
      python.field({
        name: "runtime_input_id",
        initializer: python.TypeInstantiation.uuid(nodeData.runtimeInputId),
      })
    );

    statements.push(
      python.field({
        name: "output_id",
        initializer: python.TypeInstantiation.uuid(nodeData.outputId),
      })
    );

    statements.push(
      python.field({
        name: "log_output_id",
        initializer: nodeData.logOutputId
          ? python.TypeInstantiation.uuid(nodeData.logOutputId)
          : python.TypeInstantiation.none(),
      })
    );

    return statements;
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  private async persistScriptFile(): Promise<void> {
    const filepath = this.nodeData.data.filepath ?? "./script.py";

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
      throw new Error("Expected to find code input with constant string value");
    }

    const scriptFileContents = codeInputRule.data.value ?? "";

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
    await writeFile(absolutePathToScriptFile, scriptFileContents);
    return;
  }
}
