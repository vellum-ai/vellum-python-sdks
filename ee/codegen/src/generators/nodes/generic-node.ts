import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { PromptBlock as PromptBlockSerializer } from "vellum-ai/serialization";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { PromptBlock as PromptBlockType } from "src/generators/base-prompt-block";
import { InitFile } from "src/generators/init-file";
import { NodeOutputs } from "src/generators/node-outputs";
import { NodeTrigger } from "src/generators/node-trigger";
import { BaseNode } from "src/generators/nodes/bases/base";
import { AttributeType, NODE_ATTRIBUTES } from "src/generators/nodes/constants";
import { PromptBlock } from "src/generators/prompt-block";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { FunctionArgs, GenericNode as GenericNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

export class GenericNode extends BaseNode<GenericNodeType, GenericNodeContext> {
  private functionsToGenerate: Array<{
    functionName: string;
    content: string;
  }> = [];

  private nodeAttributes: AstNode[] = [];

  // True for node that has functions in attributes
  private isNestedNode: boolean = false;

  constructor(args: BaseNode.Args<GenericNodeType, GenericNodeContext>) {
    super(args);

    this.nodeAttributes = this.generateNodeAttributes();
  }

  private generateNodeAttributes(): AstNode[] {
    const nodeAttributes = NODE_ATTRIBUTES[this.nodeData.base.name] ?? {};

    const nodeAttributesStatements: AstNode[] = [];

    this.nodeData.attributes.forEach((attribute) => {
      const attributeConfig = nodeAttributes[attribute.name];
      switch (attributeConfig?.type) {
        case AttributeType.Functions: {
          this.isNestedNode = true;
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

            nodeAttributesStatements.push(
              python.field({
                name: attribute.name,
                initializer: python.TypeInstantiation.list(
                  functionNames.map((name) => {
                    const snakeName = toPythonSafeSnakeCase(name);
                    return python.reference({
                      name: snakeName,
                      modulePath: [`.${snakeName}`],
                    });
                  })
                ),
              })
            );
          }
          break;
        }
        case AttributeType.PromptBlocks: {
          const blocks = attribute.value;

          if (
            blocks &&
            blocks.type === "CONSTANT_VALUE" &&
            blocks.value?.type === "JSON"
          ) {
            const rawBlocks = blocks.value.value as PromptBlockSerializer.Raw[];
            const deserializedBlocks: PromptBlockType[] = rawBlocks.map(
              (block) => {
                const parseResult = PromptBlockSerializer.parse(block);
                if (parseResult.ok) {
                  // TODO: Remove `as` once other types of blocks are supported
                  return parseResult.value as PromptBlockType;
                } else {
                  throw new Error(
                    `Failed to parse block ${JSON.stringify(
                      parseResult.errors
                    )}`
                  );
                }
              }
            );

            nodeAttributesStatements.push(
              python.field({
                name: attribute.name,
                initializer: python.TypeInstantiation.list(
                  deserializedBlocks.map((block) => {
                    return new PromptBlock({
                      workflowContext: this.workflowContext,
                      promptBlock: block,
                    });
                  }),
                  {
                    endWithComma: true,
                  }
                ),
              })
            );
          }
          break;
        }
        default:
          nodeAttributesStatements.push(
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

    return nodeAttributesStatements;
  }

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

    statements.push(...this.nodeAttributes);

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

  private isExcludedModulePath(): boolean {
    const baseModulePath = this.nodeData.base?.module;
    if (!baseModulePath) {
      return false;
    }

    return [
      this.workflowContext.sdkModulePathNames.CORE_NODES_MODULE_PATH,
      this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH,
      this.workflowContext.sdkModulePathNames.EXPERIMENTAL_NODES_MODULE_PATH,
    ].some((excludedPath) =>
      excludedPath.every((part, index) => baseModulePath[index] === part)
    );
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
  }

  public async persist(): Promise<void> {
    // Exclude nodes in the core, displayable, or experimental modules
    if (!this.isExcludedModulePath()) {
      const modulePath = this.getModulePath();
      const fileName = modulePath[modulePath.length - 1] + ".py";

      const relativePath = `nodes/${fileName}`;

      this.workflowContext.addPythonCodeMergeableNodeFile(relativePath);
    }

    if (this.isNestedNode) {
      // Create __init__.py for node implementation
      const nodeInitFile = new InitFile({
        workflowContext: this.workflowContext,
        modulePath: this.nodeContext.nodeModulePath,
        statements: [this.generateNodeClass()],
      });

      // Create __init__.py for node display
      const displayInitFile = new InitFile({
        workflowContext: this.workflowContext,
        modulePath: this.nodeContext.nodeDisplayModulePath,
        statements: this.generateNodeDisplayClasses(),
      });

      await Promise.all([
        nodeInitFile.persist(),
        displayInitFile.persist(),
        this.generateFunctionFiles(),
      ]);
    } else {
      await super.persist();
    }
  }

  private async generateFunctionFiles(): Promise<void> {
    const absolutePath = this.workflowContext.absolutePathToOutputDirectory;
    const basePath = this.nodeContext.nodeModulePath.join("/");

    const nodeDir = join(absolutePath, basePath);
    await mkdir(nodeDir, { recursive: true });

    await Promise.all(
      this.functionsToGenerate.map(async (funcFile) => {
        const fileName = `${toPythonSafeSnakeCase(funcFile.functionName)}.py`;
        const filepath = join(nodeDir, fileName);

        await writeFile(filepath, funcFile.content);
      })
    );
  }
}
