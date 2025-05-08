import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { FunctionDefinition } from "vellum-ai/api";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeOutputs } from "src/generators/node-outputs";
import { NodeTrigger } from "src/generators/node-trigger";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { GenericNode as GenericNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

interface FunctionArgs {
  src: string;
  definition: FunctionDefinition;
}

export class GenericNode extends BaseSingleFileNode<
  GenericNodeType,
  GenericNodeContext
> {
  private functionsToGenerate: Array<{
    functionName: string;
    content: string;
  }> = [];
  getNodeDecorators(): python.Decorator[] | undefined {
    if (!this.nodeData.adornments) {
      return [];
    }
    return this.nodeData.adornments.map((adornment) =>
      python.decorator({
        callable: python.invokeMethod({
          methodReference: python.reference({
            name: adornment.base.name,
            attribute: ["wrap"],
            modulePath: adornment.base.module,
          }),
          arguments_: adornment.attributes.map((attr) =>
            python.methodArgument({
              name: attr.name,
              value: new WorkflowValueDescriptor({
                workflowValueDescriptor: attr.value,
                nodeContext: this.nodeContext,
                workflowContext: this.workflowContext,
                iterableConfig: { endWithComma: false },
              }),
            })
          ),
        }),
      })
    );
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    this.nodeData.attributes.forEach((attribute) => {
      if (attribute.name === "functions") {
        const value = attribute.value;

        if (
          value?.type === "CONSTANT_VALUE" &&
          value.value?.type === "JSON" &&
          Array.isArray(value.value.value)
        ) {
          const functions: Array<FunctionArgs> = value.value.value;
          this.generateFunctionFile(functions);

          const functionNames: string[] = [];
          functions.forEach((f) => {
            if (f.definition && f.definition.name) {
              functionNames.push(f.definition.name);
            }
          });
          const nodeName = this.nodeContext.getNodeLabel();

          statements.push(
            python.field({
              name: "functions",
              initializer: python.TypeInstantiation.list(
                functionNames.map((name) => {
                  const snakeName = toPythonSafeSnakeCase(name);
                  return python.reference({
                    name: snakeName,
                    modulePath: [
                      `.${toPythonSafeSnakeCase(nodeName)}.${snakeName}`,
                    ],
                  });
                })
              ),
            })
          );
        }
      } else {
        statements.push(
          python.field({
            name: toPythonSafeSnakeCase(attribute.name),
            initializer: new WorkflowValueDescriptor({
              nodeContext: this.nodeContext,
              workflowValueDescriptor: attribute.value,
              workflowContext: this.workflowContext,
            }),
          })
        );
      }
    });

    if (this.nodeData.trigger.mergeBehavior !== "AWAIT_ATTRIBUTES") {
      statements.push(
        new NodeTrigger({
          nodeTrigger: this.nodeData.trigger,
          nodeContext: this.nodeContext,
        })
      );
    }

    if (this.nodeData.outputs.length > 0) {
      statements.push(
        new NodeOutputs({
          nodeOutputs: this.nodeData.outputs,
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
        })
      );
    }

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  protected getErrorOutputId(): string | undefined {
    return undefined;
  }

  private getModulePath(): string[] {
    return this.nodeContext.nodeModulePath;
  }

  private async generateFunctionFile(
    functions: Array<FunctionArgs>
  ): Promise<void> {
    functions.forEach((f) => {
      if (f.definition?.name) {
        this.functionsToGenerate.push({
          functionName: f.definition.name,
          content: f.src,
        });
      }
    });

    if (this.functionsToGenerate.length > 0) {
      this.functionsToGenerate.push({
        functionName: "__init__",
        content: "# Generated __init__.py\n",
      });

      const absolutePath = this.workflowContext.absolutePathToOutputDirectory;
      const nodeName = this.nodeContext.getNodeLabel();

      const baseModule = this.workflowContext.moduleName;
      const basePath = `${baseModule}/nodes/${toPythonSafeSnakeCase(nodeName)}`;

      const nodeDir = join(absolutePath, basePath);
      await mkdir(nodeDir, { recursive: true });

      await Promise.all(
        this.functionsToGenerate.map(async (funcFile) => {
          let filepath: string;

          if (funcFile.functionName === "__init__") {
            filepath = join(nodeDir, "__init__.py");
          } else {
            const fileName = `${toPythonSafeSnakeCase(
              funcFile.functionName
            )}.py`;
            filepath = join(nodeDir, fileName);
          }

          await writeFile(filepath, funcFile.content);
        })
      );
    }
  }

  public async persist(): Promise<void> {
    // Exclude nodes in the core, displayable, or experimental modules
    const baseModulePath = this.nodeData.base?.module;
    if (baseModulePath) {
      const isExcludedPath = [
        this.workflowContext.sdkModulePathNames.CORE_NODES_MODULE_PATH,
        this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH,
        this.workflowContext.sdkModulePathNames.EXPERIMENTAL_NODES_MODULE_PATH,
      ].some((excludedPath) =>
        excludedPath.every((part, index) => baseModulePath[index] === part)
      );

      if (!isExcludedPath) {
        const modulePath = this.getModulePath();
        const fileName = modulePath[modulePath.length - 1] + ".py";

        const relativePath = `nodes/${fileName}`;

        this.workflowContext.addPythonCodeMergeableNodeFile(relativePath);
      }
    }

    await super.persist();
  }
}
