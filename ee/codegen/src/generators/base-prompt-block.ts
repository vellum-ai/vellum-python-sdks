import { isNil } from "lodash";
import {
  AudioPromptBlock,
  ChatMessagePromptBlock,
  DocumentPromptBlock,
  ImagePromptBlock,
  JinjaPromptBlock,
  PlainTextPromptBlock,
  RichTextPromptBlock,
  VariablePromptBlock,
  VideoPromptBlock,
} from "vellum-ai/api";

import { Json } from "./json";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { WorkflowContext } from "src/context/workflow-context";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
import {
  FunctionDefinitionPromptTemplateBlock,
  PlainTextPromptTemplateBlock,
  PromptTemplateBlock,
} from "src/types/vellum";

export type PromptTemplateBlockExcludingFunctionDefinition =
  | Exclude<PromptTemplateBlock, FunctionDefinitionPromptTemplateBlock>
  | PlainTextPromptTemplateBlock;

export type PromptBlock =
  | JinjaPromptBlock
  | ChatMessagePromptBlock
  | VariablePromptBlock
  | PlainTextPromptBlock
  | RichTextPromptBlock
  | AudioPromptBlock
  | VideoPromptBlock
  | ImagePromptBlock
  | DocumentPromptBlock;

export declare namespace BasePromptBlock {
  interface Args<
    T extends PromptTemplateBlockExcludingFunctionDefinition | PromptBlock
  > {
    workflowContext: WorkflowContext;
    promptBlock: T;
    inputVariableNameById?: Record<string, string>;
  }
}

export abstract class BasePromptBlock<
  T extends PromptTemplateBlockExcludingFunctionDefinition | PromptBlock
> extends AstNode {
  protected workflowContext: WorkflowContext;
  private astNode: ClassInstantiation;
  protected inputVariableNameById: Record<string, string> | undefined; // Stateful prompt blocks have an input variable name by id, prompt blocks do not

  public constructor({
    workflowContext,
    promptBlock,
    inputVariableNameById,
  }: BasePromptBlock.Args<T>) {
    super();
    this.workflowContext = workflowContext;
    this.inputVariableNameById = inputVariableNameById;
    this.astNode = this.generateAstNode(promptBlock);
  }

  protected generateAstNode(promptBlock: T): ClassInstantiation {
    switch (promptBlock.blockType) {
      case "JINJA":
        return this.generateJinjaPromptBlock(
          promptBlock as Extract<T, { blockType: "JINJA" }>
        );
      case "CHAT_MESSAGE":
        return this.generateChatMessagePromptBlock(
          promptBlock as Extract<T, { blockType: "CHAT_MESSAGE" }>
        );
      case "VARIABLE":
        return this.generateVariablePromptBlock(
          promptBlock as Extract<T, { blockType: "VARIABLE" }>
        );
      case "RICH_TEXT":
        return this.generateRichTextPromptBlock(
          promptBlock as Extract<T, { blockType: "RICH_TEXT" }>
        );
      case "PLAIN_TEXT":
        return this.generatePlainTextPromptBlock(
          promptBlock as Extract<T, { blockType: "PLAIN_TEXT" }>
        );
      case "AUDIO":
        return this.generateAudioPromptBlock(
          promptBlock as Extract<T, { blockType: "AUDIO" }>
        );
      case "VIDEO":
        return this.generateVideoPromptBlock(
          promptBlock as Extract<T, { blockType: "VIDEO" }>
        );
      case "IMAGE":
        return this.generateImagePromptBlock(
          promptBlock as Extract<T, { blockType: "IMAGE" }>
        );
      case "DOCUMENT":
        return this.generateDocumentPromptBlock(
          promptBlock as Extract<T, { blockType: "DOCUMENT" }>
        );
    }
  }

  protected abstract generateJinjaPromptBlock(
    promptBlock: Extract<T, { blockType: "JINJA" }>
  ): ClassInstantiation;
  protected abstract generateChatMessagePromptBlock(
    promptBlock: Extract<T, { blockType: "CHAT_MESSAGE" }>
  ): ClassInstantiation;
  protected abstract generateVariablePromptBlock(
    promptBlock: Extract<T, { blockType: "VARIABLE" }>
  ): ClassInstantiation;
  protected abstract generateRichTextPromptBlock(
    promptBlock: Extract<T, { blockType: "RICH_TEXT" }>
  ): ClassInstantiation;
  protected abstract generatePlainTextPromptBlock(
    promptBlock: Extract<T, { blockType: "PLAIN_TEXT" }>
  ): ClassInstantiation;
  protected generateAudioPromptBlock(
    promptBlock: Extract<T, { blockType: "AUDIO" }>
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const audioBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(audioBlock);
    return audioBlock;
  }

  protected generateVideoPromptBlock(
    promptBlock: Extract<T, { blockType: "VIDEO" }>
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const videoBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(videoBlock);
    return videoBlock;
  }

  protected generateImagePromptBlock(
    promptBlock: Extract<T, { blockType: "IMAGE" }>
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const imageBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(imageBlock);
    return imageBlock;
  }

  protected generateDocumentPromptBlock(
    promptBlock: Extract<T, { blockType: "DOCUMENT" }>
  ): ClassInstantiation {
    const classArgs: MethodArgument[] = [
      ...this.constructCommonClassArguments(promptBlock),
      ...this.generateCommonFileInputArguments(promptBlock),
    ];

    const documentBlock = new ClassInstantiation({
      classReference: this.getPromptBlockRef(promptBlock),
      arguments_: classArgs,
    });

    this.inheritReferences(documentBlock);
    return documentBlock;
  }

  protected getPromptBlockRef(promptBlock: T): Reference {
    let pathName;
    switch (promptBlock.blockType) {
      case "JINJA":
        pathName = "JinjaPromptBlock";
        break;
      case "CHAT_MESSAGE":
        pathName = "ChatMessagePromptBlock";
        break;
      case "VARIABLE":
        pathName = "VariablePromptBlock";
        break;
      case "RICH_TEXT":
        pathName = "RichTextPromptBlock";
        break;
      case "PLAIN_TEXT":
        pathName = "PlainTextPromptBlock";
        break;
      case "AUDIO":
        pathName = "AudioPromptBlock";
        break;
      case "VIDEO":
        pathName = "VideoPromptBlock";
        break;
      case "IMAGE":
        pathName = "ImagePromptBlock";
        break;
      case "DOCUMENT":
        pathName = "DocumentPromptBlock";
        break;
    }
    return new Reference({
      name: pathName,
      modulePath: VELLUM_CLIENT_MODULE_PATH,
    });
  }

  protected generateCommonFileInputArguments(
    promptBlock:
      | Extract<T, { blockType: "AUDIO" }>
      | Extract<T, { blockType: "VIDEO" }>
      | Extract<T, { blockType: "IMAGE" }>
      | Extract<T, { blockType: "DOCUMENT" }>
  ): MethodArgument[] {
    const classArgs: MethodArgument[] = [];

    classArgs.push(
      new MethodArgument({
        name: "src",
        value: new StrInstantiation(promptBlock.src),
      })
    );

    if (promptBlock.metadata) {
      const metadataJson = new Json(promptBlock.metadata);
      classArgs.push(
        new MethodArgument({
          name: "metadata",
          value: metadataJson,
        })
      );
    }

    return classArgs;
  }

  protected constructCommonClassArguments(promptBlock: T): MethodArgument[] {
    const args: MethodArgument[] = [];

    if (promptBlock.state && promptBlock.state !== "ENABLED") {
      args.push(
        new MethodArgument({
          name: "state",
          value: new StrInstantiation(promptBlock.state),
        })
      );
    }

    const cacheConfig = this.generateCacheConfig(promptBlock);
    if (cacheConfig) {
      args.push(
        new MethodArgument({
          name: "cache_config",
          value: cacheConfig,
        })
      );
    }

    return args;
  }

  private generateCacheConfig(promptBlock: T): AstNode | undefined {
    if (isNil(promptBlock.cacheConfig)) {
      return undefined;
    }

    if (!promptBlock.cacheConfig.type) {
      return undefined;
    }

    const cacheConfigType = new StrInstantiation(promptBlock.cacheConfig.type);

    return new ClassInstantiation({
      classReference: new Reference({
        name: "EphemeralPromptCacheConfig",
        modulePath: VELLUM_CLIENT_MODULE_PATH,
      }),
      arguments_: [
        new MethodArgument({ name: "type", value: cacheConfigType }),
      ],
    });
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
